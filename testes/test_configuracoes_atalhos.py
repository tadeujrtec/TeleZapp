# SPDX-License-Identifier: GPL-3.0-or-later
"""Filtro por categoria na tela de atalhos (com wx falso)."""
import sys

from testes import wx_falso

sys.modules["wx"] = wx_falso

from telezapp import config  # noqa: E402
from telezapp.interface import configuracoes as ic  # noqa: E402
from telezapp.nucleo import atalhos as at  # noqa: E402
from telezapp.nucleo.configuracoes import ModeloConfiguracoes  # noqa: E402


def _dialogo(modelo):
    """O necessario para preencher a lista, sem montar a janela toda."""
    d = object.__new__(ic.DialogoConfiguracoes)
    d.modelo = modelo
    d.fala = None
    d.busca_atalhos = wx_falso.TextCtrl()
    d.cx_atalho_categoria = wx_falso.Choice()
    d.cx_atalho_categoria.Set(["Todas"] + modelo.atalhos_categorias())
    d.cx_atalho_categoria.SetSelection(0)
    d.lista_atalhos = wx_falso.ListBox()
    for nome in ("btn_atalho_alterar", "btn_atalho_remover",
                 "btn_atalho_padrao"):
        setattr(d, nome, wx_falso.Button())
    return d


def _modelo(tmp_path, monkeypatch):
    monkeypatch.setenv("TELEZAPP_DADOS", str(tmp_path))
    modelo = ModeloConfiguracoes(config.Config())
    registro = at.Registro()
    registro.registrar("a", "&Alfa", "Mensagens", "Ctrl+1")
    registro.registrar("b", "&Beta", "Mídias", "Ctrl+2")
    registro.registrar("c", "&Gama", "Mensagens")
    modelo.registro = registro
    return modelo


def test_lista_comeca_com_todas_as_categorias(tmp_path, monkeypatch):
    d = _dialogo(_modelo(tmp_path, monkeypatch))
    assert d.cx_atalho_categoria.itens == ["Todas", "Mensagens", "Mídias"]
    d._atalhos_preencher()
    assert d.lista_atalhos.itens == [
        "Alfa, Mensagens: Ctrl+1",
        "Beta, Mídias: Ctrl+2",
        "Gama, Mensagens: sem atalho",
    ]


def test_filtro_por_categoria_combina_com_a_busca(tmp_path, monkeypatch):
    d = _dialogo(_modelo(tmp_path, monkeypatch))
    d.cx_atalho_categoria.SetSelection(2)       # Mídias
    d._atalhos_preencher()
    assert d.lista_atalhos.itens == ["Beta, Mídias: Ctrl+2"]
    assert d._atalhos_chave() == "b"

    d.busca_atalhos.SetValue("alfa")            # Alfa esta em Mensagens
    d._atalhos_preencher()
    assert d.lista_atalhos.itens == ["Nenhuma função encontrada."]
    d.cx_atalho_categoria.SetSelection(0)       # Todas
    d._atalhos_preencher()
    assert d.lista_atalhos.itens == ["Alfa, Mensagens: Ctrl+1"]
