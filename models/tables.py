# -*- coding: utf-8 -*-

Grupo = db.define_table('grupo',
	Field('nome', label=T('Name')),
	Field('data_sorteio', 'date', label=T('Raffle Date')),
	Field('data_revelacao', 'date', label=T('Gift Day')),
	Field('valor_maximo', 'float', label=T('Max Value (R$)')),
	Field('hash_id'),
	auth.signature
)

Usuario_Grupo = db.define_table('usuario_grupo',
	Field('id_auth_user', 'reference auth_user', label=T('User')),
	Field('id_grupo', 'reference grupo', label=T('Group'))
)

Forum = db.define_table('forum',
	Field('mensagem', 'text', label=T('Message')),
	Field('id_grupo', 'reference grupo', label=T('Group')),
	auth.signature
)

Lista_Desejos = db.define_table('lista_desejos',
	Field('presente', label=T('Wish')),
	Field('imagem', 'upload', label=T('Wish Image')),
	Field('id_auth_user', 'reference auth_user', label=T('User'))
)

Sorteio = db.define_table('sorteio',
	Field('participantes','list:reference auth_user'),
	Field('id_grupo', 'reference grupo'),
	auth.signature
	)