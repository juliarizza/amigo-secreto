# -*- coding: utf-8 -*-
from random import randint

def dono_grupo(id_grupo):
	grupo = db(Grupo.id == id_grupo).select().first()
	if auth.user and grupo.created_by == auth.user.id:
		return True
	else:
		return False

def participa_grupo(id_grupo):
	grupo = db(Grupo.id == id_grupo).select().first()
	if auth.user:
		if grupo.created_by == auth.user.id:
			return True
		elif db((Usuario_Grupo.id_grupo == id_grupo) &\
				(Usuario_Grupo.id_auth_user == auth.user.id)\
				).count():
			return True
		else:
			return False
	else:
		return False

def gerar_hash_id():
	import uuid

	hash_id = str(uuid.uuid4())[-12:]
	while db(Grupo.hash_id == hash_id).count():
		hash_id = str(uuid.uuid4())[-12:]

	return hash_id

def realizar_sorteio(participantes):
	from random import shuffle
	shuffle(participantes)
	return participantes

