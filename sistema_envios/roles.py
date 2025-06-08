from rolepermissions.roles import AbstractUserRole

class Admin(AbstractUserRole):
    available_permissions = {'cadastrar_user': True, 'excluir_user': True, 'eidtar_user': True, 'cadastrar_unid': True, 'excluir_unid': True, 'eidtar_unid': True, 'cadastrar_envio': True, 'excluir_envio': True, 'eidtar_envio': True, 'cadastrar_produto': True, 'importar_planilha': True, 'exportar_planilha': True, 'visualizar_graficos': True, 'aprovar_envio': True, 'consultar_rateio': True}

class Basic(AbstractUserRole):
    available_permissions = {'cadastrar_envio': True, 'excluir_envio': True, 'eidtar_envio': True, 'cadastrar_produto': True, 'exportar_planilha': True, 'consultar_rateio': True}

class Analista(AbstractUserRole):
    available_permissions = {'cadastrar_envio': True, 'excluir_envio': True, 'eidtar_envio': True, 'cadastrar_produto': True, 'importar_planilha': True, 'exportar_planilha': True, 'visualizar_graficos': True, 'consultar_rateio': True}

class Supervisor(AbstractUserRole):
    available_permissions = {'exportar_planilha': True, 'visualizar_graficos': True, 'aprovar_envio': True, 'consultar_rateio': True}
    