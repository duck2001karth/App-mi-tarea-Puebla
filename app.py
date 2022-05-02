from flask import Flask, redirect, render_template, request, flash, url_for, session
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import datetime
import requests

#-------------------------------------------------------------------

app = Flask(__name__)

#-------------------------------------------------------------------
#Configuraciones para firebase
cred = credentials.Certificate("acount_key_api-user.json")
fire = firebase_admin.initialize_app(cred)
app.config["SECRET_KEY"] = "6yqAI7BuPIloOGCVhGvXpCfDNkUJXe3nQYjDSrV4"
#Conexion a firestore DB = DataBase
db = firestore.client()
#Se crea la referencia de la base de datos
users_ref = db.collection("users")
tasks_ref = db.collection("tasks")
#Api web
API_KEY = "AIzaSyCdtDzFbbJEfJx9A4YPZX9WgQmvJHrZewA"
#Usuario para autentificarse por correo e email
user_authentication = False
#-------------------------------------------------------------------
#-------------------------------------------------------------------#-------------------------------------------------------------------
def login_firebas(email, password):
    credentials = {"email":email,"password":password,"returnSecureToken":True}
    response = requests.post("https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={}".format(API_KEY),data=credentials)
    if response.status_code == 200:
       #print(response.content)
       #content = response.content
       dataa = response.json()
       user_login = (dataa["localId"])
       print(user_login)
       return user_login
       #print(data)
    elif response.status_code == 400:
        print(response.content)    
    return False
    #return response.content
    #print(response.status_code)
    #print(response.content)
#-------------------------------------------------------------------#-------------------------------------------------------------------
#Leer todos los usuarios
def get_ref_user(id):
    user_ref = users_ref.document(id)
    user = user_ref.get()
    if user.exists:
        print(user.to_dict()) 
        docs_ref = user_ref.collection("tasks")
    else:
        print("Usuario no existe")    
        docs_ref = False
    return docs_ref
#-------------------------------------------------------------------
#Leer una varias tasks
def leer_tasks(ref):
   docs = ref.get() 
   all_tasks = []
   for doc in docs:
       task = doc.to_dict()
       task["id"] = doc.id
       all_tasks.append(task)
   return all_tasks
#-------------------------------------------------------------------
#Crear tarea (task)
def crear_task(ref, task):
    new_task = {"name": task,
                "check": False,
                "fecha": datetime.datetime.now()}
    ref.document().set(new_task)            
#-------------------------------------------------------------------
#Actualizar tarea (task)
def actualizar_task(ref, id):
    ref.document(id).update({"check":True})
#-------------------------------------------------------------------
#Eliminar tarea (task)
def eliminar_task(ref, id):
    resp = ref.document(id).delete()
    #print(resp)
#-------------------------------------------------------------------
#-------------------------------------------------------------------#-------------------------------------------------------------------
@app.route("/login", methods = ["GET", "POST"])
def login():
   if request.method == "GET":
      if "user_login" in session:
         return redirect(url_for("home"))
      else:
         return render_template("login.html")

   elif request.method == "POST": #POST
      #Global
      global user_authentication

      email = request.form["email"]
      password = request.form["password"]
      print(f"{email}:{password}")
      try:
         user_login = login_firebas(email, password)
         print(f"Ingreso del usuario: {user_login}")
         user_authentication = get_ref_user(user_login)
         if user_login:
            session["user_login"] = user_login
            flash("Ingresaste correctamente!")
            return redirect(url_for("home"))
         else:
            print("Sesion fallida..")
            flash("Credenciales incorrectas")
            return redirect(url_for("login"))
      except:          
          print("Sesion fallida")
          flash("Credenciales incorrectas")
          return redirect (url_for("login"))  



   #if request.method == "GET":
   #    return render_template("login.html")
   # else: 
   #POST
   #   email = request.form["email"]
   #   password = request.form["password"]
   #   print(f"{email}:{password}")
   #   try:
   #      if email == "manuel123@correo.com" and password == "admin1":
   #         print("Ingresaste correctamente! ")
   #         user_authentication = True
   #         return redirect("/")
   #      else:
   #         print("Sesion fallida..")
   #         flash("Credenciales incorrectas ")
   #   except:
   #         print("Sesion fallida")
   #         flash("Credenciales incorrectas")
   #         return redirect ("/")  


#-------------------------------------------------------------------#-------------------------------------------------------------------
@app.route("/", methods = ["GET", "POST"])
def home():
   if request.method == "GET":
      if user_authentication:
         try:
            tasks = leer_tasks(tasks_ref)
            completed = []
            incompleted = []
            for task in tasks:
               print(task["check"])
               if task["check"] == True:
                  completed.append(task)
               else:
                  incompleted.append(task)
         except:
            print("ERROR...")
            tasks = []

         response = {"completed":completed, 
                        "incompleted":incompleted,
                        "counter1":len(completed),
                        "counter2":len(incompleted)}
         return render_template("index.html", response = response)
      else:
         return redirect(url_for("login"))
   else:
      #POST
      name = request.form["name"]
      print(f"\n {name}")
      try:
         crear_task(tasks_ref, name)
         return redirect("/")
      except:
         return render_template("error.html", response = "response")                                       
#-------------------------------------------------------------------#-------------------------------------------------------------------
#Actualizar tarea
@app.route("/update/<string:id>", methods = ["GET"])
def update(id):
   print(f"\n Deseas actualizar la tarea: {id}")
   try:
      actualizar_task(tasks_ref, id)
      print("La tarea fue actualizada...")
      return redirect("/")
   except:
      return render_template("error.html", response = "response")   
#-------------------------------------------------------------------#-------------------------------------------------------------------
#Eliminar tarea
@app.route("/delete/<string:id>", methods = ["GET"])
def delete(id):
   print(f"\n Deseas eliminar la tarea: {id}")
   try:
      eliminar_task(tasks_ref, id)
      print("La tarea fue eliminada...")
      return redirect("/")
   except:
      return render_template("error.html", response = "response")
#-------------------------------------------------------------------#------------------------------------------------------------------- 
        
if __name__ == "__main__":
    app.run(debug=True)