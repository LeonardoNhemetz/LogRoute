from flask import Flask, render_template, request, redirect, url_for, make_response
import mysql.connector

app = Flask(__name__)

# Configurar a conexão com o banco de dados MySQL
db = mysql.connector.connect(
    host="seu_host_mysql",
    user="seu_usuario_mysql",
    password="sua_senha_mysql",
    database="seu_banco_de_dados_mysql"
)

cursor = db.cursor()


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Verifique se o usuário marcou a opção "lembrar"
        remember = request.form.get('remember')

        # Consultar o banco de dados para verificar as credenciais e obter patente e departamento
        query = "SELECT password, patente, departamento FROM users WHERE username = %s"
        cursor.execute(query, (username,))
        result = cursor.fetchone()

        if result is not None and result[0] == password:
            response = make_response("Login Successful!")
            if remember:
                # Defina cookies para lembrar o login, senha, patente e departamento por 7 dias
                response.set_cookie('username', username, max_age=604800)
                response.set_cookie('password', password, max_age=604800)
                response.set_cookie('patente', result[1], max_age=604800)
                response.set_cookie('departamento', result[2], max_age=604800)
            return response  # Você pode redirecionar para uma página diferente aqui

    # Se o usuário já estiver logado, redirecione para a página "main"
    if 'username' in request.cookies and 'password' in request.cookies:
        return redirect('/main')

    return render_template('index.html')


@app.route('/main')
def main():
    username = request.cookies.get('username')
    patente = request.cookies.get('patente')
    departamento = request.cookies.get('departamento')

    # Passar informações de patente e departamento para a próxima página
    return render_template('main.html', username=username, patente=patente, departamento=departamento)


if __name__ == '__main__':
    app.run(debug=True)
