# -*- coding: utf-8 -*-

# Grupo
#db.grupo = Grupo
Grupo.nome.requires = IS_NOT_EMPTY()
Grupo.data_sorteio.requires = IS_DATE()
Grupo.data_revelacao.requires = IS_DATE()
Grupo.valor_maximo.default = 0
Grupo.hash_id.readable = Grupo.hash_id.writable = False
Grupo.hash_id.default = gerar_hash_id()

# Usuario_Grupo
Usuario_Grupo.id_auth_user.requires = IS_IN_DB(db, 'auth_user.id', '%(first_name)s %(last_name)s')
Usuario_Grupo.id_grupo.requires = IS_IN_DB(db, 'grupo.id', '%(nome)s')

# Forum
Forum.mensagem.requires = IS_NOT_EMPTY()
Forum.id_grupo.requires = IS_IN_DB(db, 'grupo.id', '%(nome)s')

# Lista_Desejos
Lista_Desejos.presente.requires = IS_NOT_EMPTY()
Lista_Desejos.imagem.requires = IS_EMPTY_OR(IS_IMAGE(extensions=('jpeg', 'png')))
Lista_Desejos.id_auth_user.requires = IS_IN_DB(db, 'auth_user.id', '%(first_name)s %(last_name)s')

# Sorteio
Sorteio.participantes.requires = IS_NOT_EMPTY()
Sorteio.id_grupo.requires = IS_IN_DB(db, 'grupo.id', '%(nome)s')