from flask import render_template, url_for, redirect
from pinterest import app, database, bcrypt
from flask_login import login_required, login_user, logout_user, current_user
from pinterest.forms import FormLogin, FormCriarConta, FormFoto
from pinterest.models import Usuario, Post
import os 
from werkzeug.utils import secure_filename

@app.route("/" , methods=["GET", "POST"])
def homepage():
    form_login = FormLogin()
    if form_login.validate_on_submit():
        usuario = Usuario.query.filter_by(email=form_login.email.data).first()
        checa_senha = bcrypt.check_password_hash(usuario.senha, form_login.senha.data) 
        if usuario and checa_senha:
            login_user(usuario)
            return redirect(url_for("perfil", id_usuario=usuario.id))

    return render_template("homepage.html", form=form_login)

@app.route("/criarconta", methods=["GET", "POST"])
def criar_conta():
    form_criar_conta = FormCriarConta()
    if form_criar_conta.validate_on_submit():
        senha_criptografada = bcrypt.generate_password_hash(form_criar_conta.senha.data)
        usuario = Usuario(
            email=form_criar_conta.email.data,
            senha=senha_criptografada,
            username=form_criar_conta.username.data
        )
        database.session.add(usuario)
        database.session.commit()
        login_user(usuario, remember=True)
        return redirect(url_for("perfil", id_usuario=usuario.id))

    return render_template("criar_conta.html", form=form_criar_conta)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("homepage"))

@app.route("/perfil/<int:id_usuario>", methods=["GET", "POST"])
@login_required
def perfil(id_usuario):
    if int(id_usuario) == int(current_user.id):
        form_foto = FormFoto()
        if form_foto.validate_on_submit():
            arquivo = form_foto.foto.data
            nome_seguro = secure_filename(arquivo.filename)
            # Salvar na pasta de Posts
            caminho = os.path.join(
                os.path.abspath(
                    os.path.dirname(__file__)
                ),
                app.config["UPLOAD_FOLDER"],
                nome_seguro
            )
            arquivo.save(caminho)
            # Banco de Dados
            foto = Post(imagem=nome_seguro, id_usuario=current_user.id)
            database.session.add(foto)
            database.session.commit()
        return render_template("perfil.html", usuario=current_user, form=form_foto)
    else:
        usuario = Usuario.query.get(int(id_usuario))
        return render_template("perfil.html", usuario=usuario, form=None)
    
@app.route("/feed")
@login_required
def feed():
    fotos = Post.query.order_by(Post.data_criacao.desc()).all()
    return render_template("feed.html", fotos = fotos)