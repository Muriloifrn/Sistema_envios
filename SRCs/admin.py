from django.contrib import admin
from SRCs.models import Unidade, Usuario, Produto, Envio, Rateio

admin.site.register(Unidade)
admin.site.register(Usuario)
admin.site.register(Produto)
admin.site.register(Envio)
admin.site.register(Rateio)

# Register your models here.
