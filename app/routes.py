from flask import Blueprint, render_template, redirect, url_for, flash, request
from app import db
from app.models import User, Foro, Note, Message
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return redirect(url_for('main.login'))

@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('main.dashboard'))
        else:
            flash('Error en el inicio de sesión. Revisa tus datos.', 'danger')
    return render_template('login.html')

@main.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('¡Tu cuenta ha sido creada! Ahora puedes iniciar sesión.', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html')

@main.route('/dashboard')
@login_required
def dashboard():
    contacts = current_user.contacts.all()
    return render_template('dashboard.html', contacts=contacts)

@main.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.login'))

@main.route('/create_note', methods=['GET', 'POST'])
@login_required
def create_note():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')

        # Validación de datos
        if not title or not content:
            flash('Por favor, completa todos los campos.', 'danger')
            return redirect(url_for('main.create_note'))

        try:
            new_note = Note(title=title, content=content, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
            flash('Nota creada con éxito.', 'success')
            return redirect(url_for('main.view_notes'))
        except Exception as e:
            db.session.rollback()
            flash('Ocurrió un error al crear la nota. Inténtalo de nuevo.', 'danger')
            print(e)  # Para depuración

    return render_template('create_note.html')

@main.route('/delete_note/<int:note_id>', methods=['POST'])
@login_required
def delete_note(note_id):
    note = Note.query.get_or_404(note_id)

    if note.user_id != current_user.id:
        flash('No tienes permiso para eliminar esta nota.', 'danger')
        return redirect(url_for('main.view_notes'))

    try:
        db.session.delete(note)
        db.session.commit()
        flash('Nota eliminada con éxito.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Ocurrió un error al eliminar la nota. Inténtalo de nuevo.', 'danger')
        print(e)  # Para depuración

    return redirect(url_for('main.view_notes'))

@main.route('/view_notes')
@login_required
def view_notes():
    notes = Note.query.filter_by(user_id=current_user.id).all()
    return render_template('view_notes.html', notes=notes)

@main.route('/view_note/<int:note_id>', methods=['GET'])
@login_required
def view_note(note_id):
    # Buscar la nota por su ID
    note = Note.query.get_or_404(note_id)

    # Verificar que la nota pertenezca al usuario actual
    if note.user_id != current_user.id:
        flash('No tienes permiso para ver esta nota.', 'danger')
        return redirect(url_for('main.view_notes'))

    # Renderizar la plantilla con los detalles de la nota
    return render_template('view_note.html', note=note)

@main.route('/create_foro', methods=['GET', 'POST'])
@login_required
def create_foro():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')

        # Validación de datos
        if not title or not description:
            flash('Por favor, completa todos los campos.', 'danger')
            return redirect(url_for('main.create_foro'))

        try:
            new_foro = Foro(title=title, description=description)
            db.session.add(new_foro)
            db.session.commit()

            # Asociar el foro con el usuario actual
            current_user.foros.append(new_foro)
            db.session.commit()

            flash('Foro creado con éxito.', 'success')
            return redirect(url_for('main.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Ocurrió un error al crear el foro: {str(e)}', 'danger')  # Muestra el mensaje de error específico
            print(e)  # Para depuración

    return render_template('create_foro.html')


@main.route('/view_foros')
@login_required
def view_foros():
    # Obtener todos los foros en los que participa el usuario actual
    foros = current_user.foros.all()
    return render_template('view_foros.html', foros=foros)


@main.route('/join_foro/<int:foro_id>', methods=['POST'])
@login_required
def join_foro(foro_id):
    foro = Foro.query.get_or_404(foro_id)

    # Verificar si el usuario ya está participando en el foro
    if current_user in foro.user_participants.all():
        flash('Ya estás participando en este foro.', 'info')
    else:
        current_user.foros.append(foro)
        db.session.commit()
        flash('Te has unido al foro.', 'success')

    return redirect(url_for('main.view_foros'))


@main.route('/leave_foro/<int:foro_id>', methods=['POST'])
@login_required
def leave_foro(foro_id):
    foro = Foro.query.get_or_404(foro_id)

    # Verificar si el usuario está participando en el foro
    if current_user not in foro.user_participants.all():
        flash('No estás participando en este foro.', 'info')
    else:
        current_user.foros.remove(foro)
        db.session.commit()
        flash('Has abandonado el foro.', 'success')

    return redirect(url_for('main.view_foros'))


@main.route('/view_foro/<int:foro_id>', methods=['GET', 'POST'])
@login_required
def view_foro(foro_id):
    foro = Foro.query.get_or_404(foro_id)

    # Verificar si el usuario está participando en el foro
    if current_user not in foro.participants.all():
        flash('No tienes permiso para ver este foro.', 'info')
        return redirect(url_for('main.view_foros'))

    if request.method == 'POST':
        content = request.form.get('content')

        # Validación de datos
        if not content:
            flash('Por favor, revise de que el mensaje no se encuentre vacio.', 'danger')
        else:
            try:
                new_message = Message(content=content, user_id=current_user.id, foro_id=foro.id)
                db.session.add(new_message)
                db.session.commit()
                flash('Mensaje enviado con éxito.', 'success')
                return redirect(url_for('main.view_foro', foro_id=foro.id))
            except Exception as e:
                db.session.rollback()
                flash(f'Ocurrió un error al enviar el mensaje: {str(e)}', 'danger')
                print(e)
    
    messages = Message.query.filter_by(foro_id=foro.id).order_by(Message.id.desc()).all()
    return render_template('view_foro.html', foro=foro, messages=messages)

@main.route('/all_foros')
@login_required
def all_foros():
    #obtener todos los foros disponibles
    foros = Foro.query.all()
    return render_template('all_foros.html', foros=foros)

@main.route('/add_contact/<int:user_id>', methods=['POST'])
@login_required
def add_contact(user_id):
    user_to_add = User.query.get_or_404(user_id)

    # Verificar si el usuario ya está agregado como contacto
    if user_to_add in current_user.contacts.all():
        flash('Este usuario ya está en tus contactos.', 'info')
    else:
        current_user.contacts.append(user_to_add)
        db.session.commit()
        flash(f'{user_to_add.username} ha sido agregado a tus contactos.', 'success')

    return redirect(url_for('main.dashboard'))

@main.route('/remove_contact/<int:user_id>', methods=['POST'])
@login_required
def remove_contact(user_id):
    user_to_remove = User.query.get_or_404(user_id)

    # Verificar si el usuario está en los contactos
    if user_to_remove not in current_user.contacts.all():
        flash('Este usuario no está en tus contactos.', 'info')
    else:
        current_user.contacts.remove(user_to_remove)
        db.session.commit()
        flash(f'{user_to_remove.username} ha sido eliminado de tus contactos.', 'success')

    return redirect(url_for('main.dashboard'))