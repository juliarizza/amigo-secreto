# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
#########################################################################

def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """
    form = SQLFORM.factory(
        Field('nome', label=T('Name'), requires=IS_NOT_EMPTY()),
        Field('email', label=T('E-mail'), requires=IS_EMAIL()),
        Field('mensagem', 'text', label=T('Message'), requires=IS_NOT_EMPTY())
        )
    if form.process().accepted:
        mail.send(
            to=["you@gmail.com"],
            reply_to=form.vars.email,
            subject="Mensagem recebida em sorteio.com",
            message="%s enviou a seguinte mensagem: %s" % (form.vars.nome, form.vars.mensagem)
            )
        response.flash = T("Message sent!")
    elif form.errors:
        response.flash = T("Form has errors!")
    return dict(form=form)


def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """
    response.title += " - "+request.args(0).replace('_',' ').title()
    if request.args(0) == 'login':
        retorno = response.render('default/login.html',dict(form=auth()))
    elif request.args(0) == 'register':
        retorno = response.render('default/register.html',dict(form=auth()))
    elif request.args(0) == 'retrieve_password':
        retorno = response.render('default/retrieve_psw.html',dict(form=auth()))
    else:
        retorno = response.render('default/user.html',dict(form=auth()))
    return retorno


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


## Páginas da App

## Grupo
@auth.requires_login()
def dashboard():
    participa_em = []
    for grupo in db(Grupo).select():
        if participa_grupo(grupo.id) or dono_grupo(grupo.id):
            participa_em.append(grupo.id)

    grupos = db(Grupo.id.belongs(participa_em)).select()
    return dict(grupos=grupos)

@auth.requires(lambda: dono_grupo(request.args(0, cast=int)) or participa_grupo(request.args(0,cast=int))\
                        or auth.has_membership('Administrador'))
def grupo():
    response.title += ' - Grupo'
    id_grupo = request.args(0, cast=int)
    grupo = db(Grupo.id == id_grupo).select().first()
    p = db(Usuario_Grupo.id_grupo == id_grupo).select()
    
    participantes = [x.id_auth_user for x in p]
    participantes.append(grupo.created_by)

    sorteio = db(Sorteio.id_grupo == grupo.id).select().first()

    return dict(grupo=grupo, participantes=participantes, sorteio=sorteio)

@auth.requires_login()
def novo_grupo():
    response.title += ' - Novo Grupo'
    form = crud.create(Grupo)

    for el in form.elements():
        if el['_type'] == 'text':
            el['_class'] = 'form-control'
        elif el in form.elements("label"):
            el['_class'] = 'sub-title'
        elif el['_type'] == 'submit':
            el['_class'] = 'btn btn-success'
            el['_style'] = 'margin-top: 20px;'
            
    return dict(form=form)

@auth.requires(lambda: dono_grupo(request.args(0, cast=int)) or auth.has_membership('Administrador'))
def atualizar_grupo():
    response.title += ' - Atualizar Grupo'
    id_grupo = request.args(0, cast=int)
    form = crud.update(Grupo, id_grupo)

    for el in form.elements():
        if el['_type'] == 'text':
            el['_class'] = 'form-control'
        elif el in form.elements("label"):
            el['_class'] = 'sub-title'
        elif el['_type'] == 'submit':
            el['_class'] = 'btn btn-success'
            el['_style'] = 'margin-top: 20px;'
    return dict(form=form)

@auth.requires(lambda: dono_grupo(request.args(0, cast=int)) or auth.has_membership('Administrador'))
def apagar_grupo():
    id_grupo = request.args(0, cast=int)
    db(Grupo.id == id_grupo).delete()
    redirect(URL('dashboard'))

@auth.requires(lambda: dono_grupo(request.args(0, cast=int)) or \
    participa_grupo(request.args(0, cast=int)) or \
    auth.has_membership('Administrador'))
def convidar_amigo():
    id_grupo = request.args(0, cast=int)
    grupo = db(Grupo.id == id_grupo).select().first()
    form = SQLFORM.factory(
        Field('nome', label="Nome do Amigo"),
        Field('email', label="Email do Amigo")
        )
    if form.process().accepted:
        mail.send(
            to = form.vars.email,
            subject = "Você foi convidado para um grupo de Amigo Secreto!",
            message = """
            Você foi convidado para um grupo de Amigo Secreto por %s %s. Para participar, acesse:
            %s
            """ % (auth.user.first_name, auth.user.last_name, URL('adicionar_amigo', args=grupo.hash_id, host=True, scheme=True))
            )

    return dict(form=form)

@auth.requires_login()
def adicionar_amigo():
    hash_grupo = request.args(0)
    grupo = db(Grupo.hash_id == hash_grupo).select().first()
    if not db((Usuario_Grupo.id_grupo == grupo.id)&\
              (Usuario_Grupo.id_auth_user == auth.user.id)).count()\
        and not grupo.created_by == auth.user.id:
        Usuario_Grupo.insert(id_auth_user=auth.user.id,id_grupo=grupo.id)

    redirect(URL('grupo', args=grupo.id))

def sortear():
    id_grupo = request.args(0, cast=int)
    grupo = db(Grupo.id == id_grupo).select().first()
    p = db(Usuario_Grupo.id_grupo == id_grupo).select()

    participantes = [x.id_auth_user for x in p]
    participantes.append(grupo.created_by)

    r = realizar_sorteio(participantes)
    if db(Sorteio.id_grupo == id_grupo).count():
        db(Sorteio.id_grupo == id_grupo).update(participantes=r)
    else:
        Sorteio.insert(participantes=r,id_grupo=id_grupo)

    for p in participantes:
        if participantes.index(p) == len(participantes)-1:
            amigo = participantes[0]
        else:
            amigo = participantes[participantes.index(p)+1]
        mail.send(
            to=p.email,
            subject="Resultado do Amigo Secreto",
            message="Você saiu com %s %s" % (amigo.first_name, amigo.last_name)
            )
    redirect(URL('grupo',args=id_grupo))

## Forum
@auth.requires(lambda: participa_grupo(request.args(0, cast=int)) or auth.has_membership("Administrador"))
def forum():
    response.title += ' - Fórum'
    id_grupo = request.args(0, cast=int)
    
    ## paginação
    if not request.vars.page or int(request.vars.page) <= 0:
        redirect(URL(args=request.args, vars={'page':1}))
    else:
        pagina = int(request.vars.page)

    inicio = (pagina-1)*10
    fim = pagina*10

    ## busca
    if request.vars.q:
        q = request.vars.q
        mensagens = db((Forum.id_grupo == id_grupo)&(Forum.mensagem.like('%'+q+'%'))).select(orderby=~Forum.created_on, limitby=(inicio,fim))
    else:
        mensagens = db(Forum.id_grupo == id_grupo).select(orderby=~Forum.created_on, limitby=(inicio,fim))

    ## validação da paginação
    qtd_pags = (db(Forum.id_grupo == id_grupo).count()/10)+1
    if int(request.vars.page) > qtd_pags:
        redirect(URL(args=request.args,vars={'page':qtd_pags}))
    
    Forum.id_grupo.default = id_grupo
    Forum.id_grupo.writable = Forum.id_grupo.readable = False
    
    form = SQLFORM(Forum)
    if form.process().accepted:
        session.flash = T("Message sent!")
        redirect(URL('forum', args=id_grupo))
    elif form.errors:
        response.flash = T("Form has errors!")

    return dict(mensagens=mensagens, form=form)

@auth.requires(lambda: db(Forum.id == request.args(0, cast=int)).select().first().created_by == auth.user.id \
                or auth.has_membership("Administrador"))
def editar_mensagem():
    response.title += ' - Editar Mensagem'
    id_registro = request.args(0, cast=int)

    Forum.id_grupo.writable = Forum.id_grupo.readable = False

    form = crud.update(Forum, id_registro)
    return dict(form=form, id_grupo=db(Forum.id == id_registro).select().first().id_grupo)

@auth.requires(lambda: db(Forum.id == request.args(0, cast=int)).select().first().created_by == auth.user.id \
                or auth.has_membership("Administrador"))
def apagar_mensagem():
    id_registro = request.args(0, cast=int)
    msg = db(Forum.id == id_registro).select().first()
    id_grupo = msg.id_grupo
    db(Forum.id == id_registro).delete()
    redirect(URL('forum', args=[id_grupo]))

## Lista de Desejos

def desejos():
    response.title += " - Lista de Desejos"

    id_usuario = request.args(0, cast=int)
    desejos = db(Lista_Desejos.id_auth_user == id_usuario).select()
    usuario = db(db.auth_user.id == id_usuario).select().first()
    return dict(desejos=desejos, usuario=usuario)

def novo_desejo():
    response.title += ' - Novo Desejo'
    id_usuario = request.args(0, cast=int)

    Lista_Desejos.id_auth_user.default = id_usuario
    Lista_Desejos.id_auth_user.writable = False
    Lista_Desejos.id_auth_user.readable = False

    form = crud.create(Lista_Desejos)
    return dict(form=form)

def editar_desejo():
    response.title += ' - Editar Desejo'
    id_registro = request.args(0, cast=int) 

    Lista_Desejos.id_auth_user.writable = False
    Lista_Desejos.id_auth_user.readable = False

    form = crud.update(Lista_Desejos, id_registro)
    return dict(form=form)

def apagar_desejo():
    id_registro = request.args(0, cast=int)
    desejo = db(Lista_Desejos.id == id_registro).select().first()
    db(Lista_Desejos.id == id_registro).delete()
    redirect(URL('desejos', args=[desejo.id_auth_user]))