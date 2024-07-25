from flask import Flask, render_template, request, redirect, url_for, flash
from sqlalchemy.exc import SQLAlchemyError
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import distinct
import psycopg2
from pprint import pprint

app = app = Flask(__name__)
app.config["SECRET_KEY"] = "Secret"

# Configuración de la base de datos PostgreSQL
# postgresql://postgres:WeLZnkiKBsfVFvkaRHWqfWtGzvmSnOUn@viaduct.proxy.rlwy.net:35149/railway
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:WeLZnkiKBsfVFvkaRHWqfWtGzvmSnOUn@viaduct.proxy.rlwy.net:35149/railway'
app.config['SQLALCHEMY_BINDS'] = {
    'db2': 'postgresql://postgres:aAB2Be35CBAd2GgA5*DdC45FaCf26G44@viaduct.proxy.rlwy.net:58920/railway',  # Base de EMPLEADOS
    'db3': 'postgresql://postgres:E6C13EfeAbaFd2GA4fgCcAdC*g13324B@monorail.proxy.rlwy.net:25301/railway',  # Base de logistica
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# try:
# connection = psycopg2.connect(
# host= 'localhost',
# user = 'postgres',
# password = 'cel123',
# database = 'Prueba',
# port = '5432'
# )
# print (" Conexion exitosa")
# except Exception as ex:
# print (ex)


db = SQLAlchemy(app)
# definimos el modelo para la tabla y mapeamos la tabla dispositivos
# debemos especificar el es quema en la base de datos para encontrar la tabla solicitada

class Empleados(db.Model):
    __bind_key__ = 'db2'
    

    # Campos de la tabla Empleados
    id = db.Column(db.String(100), primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    sede = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(60), nullable=False)
    isAdmin = db.Column(db.Boolean, default=False)
    jefeTienda = db.Column(db.Boolean, default=False)
    isSede = db.Column(db.Boolean, default=False)
    isTV = db.Column(db.Boolean, default=False)
    password_secret=db.Column(db.String(60))
    cedula=db.Column(db.String(100))
    cargo=db.Column(db.Enum('Admin', 'jefeTienda', 'Sede','TV','servicioTecnico','vendedorMedellin','vendedorBogota','encargadoBodega','domiciliario','RH',name='cargo'))


class Dispositivos(db.Model):
    __tablename__ = 'dispositivos'
    __table_args__ = {'schema': 'activos_ti'}
    idusuario = db.Column(db.Integer, primary_key=True)
    area = db.Column(db.String(100), nullable=False)
    colaborador = db.Column(db.String(100), nullable=False)
    sede = db.Column(db.String(100), nullable=False)
    modelo = db.Column(db.String(100), nullable=False)
    serial = db.Column(db.String(100), nullable=False)
    movil = db.Column(db.String(100))
    contrasena = db.Column(db.String(100), nullable=False)
    fechaCompra = db.Column(db.Date, nullable=False)
    estado = db.Column(db.String(100), nullable=False)
    tipoActivo = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(100), nullable=False)
    notas = db.Column(db.Text, nullable=True)
    activos = db.Column(db.Boolean, default=True)
    #habilitado= db.Column(db.Boolean, nullable=False,default=True)


# creamos la ruta utilizando los metodos http
@app.route("/escritorio", methods=["GET", "POST"])
def ingreso():
    if request.method == "POST":
        if 'toggle_active' in request.form:
            idusuario = request.form.get('idusuario')
            dispositivo = Dispositivos.query.get_or_404(idusuario)
            dispositivo.activos = not dispositivo.activos
            try:
                db.session.commit()
                flash("Estado del dispositivo actualizado", "success")
            except SQLAlchemyError as e:
                db.session.rollback()
                flash(f"Error al actualizar el estado del dispositivo: {str(e)}", "error")
            return redirect(url_for('escritorio'))
        
        try:
            nuevo_dispositivo = Dispositivos(
                area=request.form["area"],
                sede=request.form["sede"],
                modelo=request.form["modelo_marca"],
                colaborador=request.form["colaborador"],
                serial=request.form["serial"],
                contrasena=request.form["contrasena"],
                fechaCompra=request.form["fecha_compra"],
                estado=request.form["estado"],
                tipoActivo=request.form["tipo_activo"],
                correo=request.form["correo"],
                notas=request.form["notas"],
                activos=True  # Asumiendo que los dispositivos nuevos siempre se ingresan como activos
            )
            db.session.add(nuevo_dispositivo)
            db.session.commit()
            flash("Información guardada con éxito", "success")
            return redirect(url_for('activos'))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f"Error al enviar la información: {str(e)}", "error")
    
    # Filtrar solo dispositivos activos para mostrar en la tabla
    dispositivos = Dispositivos.query.filter_by(activos=True, tipoActivo='Escritorio').all()
    
    return render_template('activos.html', dispositivos=dispositivos)


@app.route('/')  # Ruta principal
def index():
    # Redirigir a la página de ingreso de activos
    return redirect(url_for('ingresoactivos'))


@app.route('/ingresoactivos', methods=['GET', 'POST'])
def ingresoactivos():
    if request.method == "POST":
        try:
            movil = request.form.get("movil", "")
            tipo_activo = request.form.get("tipo_activo")
            
            # Si el tipo de activo no es Smartphone, establecemos movil como una cadena vacía
            if tipo_activo != "Smartphone":
                movil = ""
            nuevo_dispositivo = Dispositivos(
                area=request.form["area"],
                sede=request.form["sede"],
                modelo=request.form["modelo_marca"],
                colaborador=request.form["colaborador"],
                serial=request.form["serial"],
                movil=request.form["movil"],
                contrasena=request.form["contrasena"],
                fechaCompra=request.form["fecha_compra"],
                estado=request.form["estado"],
                tipoActivo=request.form["tipo_activo"],
                correo=request.form["correo"],
                notas=request.form["notas"]
            )
            db.session.add(nuevo_dispositivo)
            db.session.commit()
            mensaje = f"El dispositivo {
                nuevo_dispositivo.modelo} registrado exitosamente."
            flash(mensaje, "success")
            return redirect(url_for('ingresoactivos'))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f"Error al enviar la información: {str(e)}", "danger")
            # No retornamos aquí, dejamos que continúe al código después del if
            # Este código se ejecutará tanto para GET como para POST después de un error
            
    dispositivos = Dispositivos.query.all()
    colaboradores = Colaboradores.query.order_by(Colaboradores.nombres).all()
    return render_template('ingresoactivos.html', dispositivos=dispositivos, colaboradores=colaboradores)


@app.route("/activos", methods=["GET", "POST"])
def activos():
    if request.method == "POST":
        if 'toggle_active' in request.form:
            # Manejar la activación/desactivación
            idusuario = request.form.get('idusuario')
            dispositivo = Dispositivos.query.get_or_404(idusuario)
            dispositivo.activos = not dispositivo.activos
            try:
                db.session.commit()
                flash("Estado del dispositivo actualizado", "success")
            except SQLAlchemyError as e:
                db.session.rollback()
                flash(f"Error al actualizar el estado del dispositivo: {str(e)}", "error")
            return redirect(url_for('activos'))
        
        try:
            nuevo_dispositivo = Dispositivos(
                area=request.form["area"],
                sede=request.form["sede"],
                modelo=request.form["modelo_marca"],
                colaborador=request.form["colaborador"],
                serial=request.form["serial"],
                contrasena=request.form["contrasena"],
                fechaCompra=request.form["fecha_compra"],
                estado=request.form["estado"],
                tipoActivo=request.form["tipo_activo"],
                correo=request.form["correo"],
                notas=request.form["notas"]
            )
            db.session.add(nuevo_dispositivo)
            db.session.commit()
            flash("Información guardada con éxito", "success")
            return redirect(url_for('activos'))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f"Error al enviar la información: {str(e)}", "error")
# realizamos la consulta y que solo nos muestre los activos
    dispositivos = Dispositivos.query.filter_by(activos=True).all()
    return render_template('activos.html', dispositivos=dispositivos)


class Colaboradores(db.Model):
    __tablename__ = 'colaboradores'
    __table_args__ = {'schema': 'activos_ti'}
    idcolaborador = db.Column(db.Integer, primary_key=True)
    nombres = db.Column(db.String(100), nullable=False)


@app.route('/actualizar/<int:idusuario>', methods=['GET', 'POST'])
def actualizar(idusuario):
    dispositivo = Dispositivos.query.get_or_404(idusuario)
   
    # Obtener todos los colaboradores únicos
    colaboradores = db.session.query(Dispositivos.colaborador).distinct().all()
    colaboradores = [c[0] for c in colaboradores if c[0]]  # Eliminar valores nulos o vacíos
   
    if request.method == 'POST':
        try:
            dispositivo.area = request.form['area']
            dispositivo.sede = request.form['sede']
            dispositivo.modelo = request.form['modelo_marca']
            dispositivo.colaborador = request.form['colaborador']
            dispositivo.serial = request.form['serial']
            dispositivo.movil = request.form.get('movil')
            dispositivo.contrasena = request.form['contrasena']
            dispositivo.fechaCompra = request.form['fecha_compra']
            dispositivo.estado = request.form['estado']
            dispositivo.tipoActivo = request.form['tipo_activo']
            dispositivo.correo = request.form['correo']
            dispositivo.notas = request.form.get('notas')
           
            db.session.commit()
            flash('Dispositivo actualizado con éxito', 'success')
            return redirect(url_for('activos'))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'Error al actualizar el dispositivo: {str(e)}', 'error')
   
    return render_template('actualizar.html', dispositivo=dispositivo, colaboradores=colaboradores)

@app.route('/escritorio')
def escritorio():
    return render_template('escritorio.html')

@app.route('/colaboradores')
def colaborador():
    return render_template("colaboradores.html")


@app.route('/portatiles', methods=["GET", "POST"])
def portatiles():
    if request.method == "POST":
        if 'toggle_active' in request.form:
            idusuario = request.form.get('idusuario')
            dispositivo = Dispositivos.query.get_or_404(idusuario)
            dispositivo.activos = not dispositivo.activos
            try:
                db.session.commit()
                flash("Estado del dispositivo actualizado", "success")
            except SQLAlchemyError as e:
                db.session.rollback()
                flash(f"Error al actualizar el estado del dispositivo: {str(e)}", "error")
            return redirect(url_for('activos'))
        
        try:
            nuevo_dispositivo = Dispositivos(
                area=request.form["area"],
                sede=request.form["sede"],
                modelo=request.form["modelo_marca"],
                colaborador=request.form["colaborador"],
                serial=request.form["serial"],
                contrasena=request.form["contrasena"],
                fechaCompra=request.form["fecha_compra"],
                estado=request.form["estado"],
                tipoActivo=request.form["tipo_activo"],
                correo=request.form["correo"],
                notas=request.form["notas"],
                activos=True  # Asumiendo que los dispositivos nuevos siempre se ingresan como activos
            )
            db.session.add(nuevo_dispositivo)
            db.session.commit()
            flash("Información guardada con éxito", "success")
            return redirect(url_for('activos'))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f"Error al enviar la información: {str(e)}", "error")
    
    # Filtrar solo dispositivos activos para mostrar en la tabla
    dispositivos = Dispositivos.query.filter_by(activos=True, tipoActivo='Portatil').all()
    
    return render_template('activos.html', dispositivos=dispositivos)


@app.route('/impresoras', methods= ["GET", "POST"])
def impresoras():
    dispositivos = Dispositivos.query.filter_by(tipoActivo="Impresora").all()
    if request.method == "POST":

        nuevo_dispositivo = Dispositivos(
            area=request.form["area"],
            colaborador=request.form["colaboradores"],
            sede=request.form["sede"],
            modelo=request.form["modelo_marca"],
            serial=request.form["serial"],
            movil=request.form["movil"],
            contraseña=request.form["contrasena"],
            fechacompra=request.form["fecha_compra"],
            estado=request.form["estado"],
            tipoactivo=request.form["tipo_activo"],
            correo=request.form["correo"],
            notas=request.form["notas"]
        )
    #  agregamos los datos para luego ser guardados en la base de datos
        db.session.add(nuevo_dispositivo)
        db.session.commit()
        return "Información guardada con éxito"
    else:
        return render_template('impresora.html', dispositivos=dispositivos)


@app.route('/telefono', methods=["GET", "POST"])
def telefono():
    if request.method == "POST":
        if 'toggle_active' in request.form:
            idusuario = request.form.get('idusuario')
            dispositivo = Dispositivos.query.get_or_404(idusuario)
            dispositivo.activos = not dispositivo.activos
            try:
                db.session.commit()
                flash("Estado del dispositivo actualizado", "success")
            except SQLAlchemyError as e:
                db.session.rollback()
                flash(f"Error al actualizar el estado del dispositivo: {str(e)}", "error")
            return redirect(url_for('activos'))
        
        try:
            nuevo_dispositivo = Dispositivos(
                area=request.form["area"],
                sede=request.form["sede"],
                modelo=request.form["modelo_marca"],
                colaborador=request.form["colaborador"],
                serial=request.form["serial"],
                contrasena=request.form["contrasena"],
                fechaCompra=request.form["fecha_compra"],
                estado=request.form["estado"],
                tipoActivo=request.form["tipo_activo"],
                correo=request.form["correo"],
                notas=request.form["notas"],
                activos=True  # Asumiendo que los dispositivos nuevos siempre se ingresan como activos
            )
            db.session.add(nuevo_dispositivo)
            db.session.commit()
            flash("Información guardada con éxito", "success")
            return redirect(url_for('activos'))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f"Error al enviar la información: {str(e)}", "error")
    
    # Filtrar solo dispositivos activos para mostrar en la tabla
    dispositivos = Dispositivos.query.filter_by(activos=True, tipoActivo='Smartphone').all()
    
    return render_template('telefonos.html', dispositivos=dispositivos)
    
@app.route('/inhabilitados')
def inhabilitado():
    dispositivos_inactivos = Dispositivos.query.filter_by(activos=False).all()
    return render_template("inhabilitados.html", dispositivos=dispositivos_inactivos)


if __name__ == '__main__':
    app.run(debug=True)