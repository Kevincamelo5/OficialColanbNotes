from flask import Blueprint, render_template, redirect, url_for, flash, request
from app import db
from app.models import User, Foro, Note, Message, FriendRequest, PrivateMessage
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

@main.route('/edit_note/<int:note_id>', methods=['GET', 'POST'])
@login_required
def edit_note(note_id):
    #buscar la nota por su id
    note = Note.query.get_or_404(note_id)

    #verificar que la nota pertenezca al usuario actual
    if note.user_id != current_user.id:
        flash('No tienes permiso para editar esta nota.', 'danger')
        return redirect(url_for('main.view_notes'))
    
    if request.method == 'POST':
        #obtener los datos del formulario
        new_title = request.form.get('title')
        new_content = request.form.get('content')

        if not new_title or not new_content:
            flash('Por favor, completa todos los campos.', 'danger')
            return redirect(url_for('main.edit_note', note_id=note.id))
        
        try:
            note.title = new_title
            note.content = new_content
            db.session.commit()
            flash("Nota actualizada con exito.", 'success')
            return redirect(url_for('main.view_note', note_id=note.id))
        except Exception as e:
            db.session.rollback()
            flash(f'ocurrio un error al actualizar la nota: {str(e)}', 'danger')
            print(e) #para depuracion

    return render_template('edit_note.html', note=note)

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

    # Verificar si el usuario está autenticado
    if not current_user.is_authenticated:
        flash('Debes iniciar sesión para ver los foros.', 'danger')
        return redirect(url_for('main.login'))
    
     #obtener el termino de busqueda del parametro query
    query = request.args.get('query', '').strip()
    if query:
        # Filtrar los foros por el término de búsqueda
        all_foros = Foro.query.filter((Foro.title.ilike(f'%{query}%')) | (Foro.description.ilike(f'%{query}'))).all()
    else:
        all_foros = Foro.query.all()
    
    # Obtener los foros en los que el usuario ya está participando
    user_foros = current_user.foros.all()
    
    # Filtrar los foros disponibles excluyendo los que el usuario ya está participando
    available_foros = [foro for foro in all_foros if foro not in user_foros]
    
    return render_template('all_foros.html', foros=available_foros)

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

@main.route('/search_users', methods=['GET', 'POST'])
@login_required
def search_users():
    query = request.args.get('query', '').strip()
    if query:
        users = User.query.filter(
            (User.username.ilike(f'%{query}%')) | (User.email.ilike(f'%{query}%'))
        ).all()
    else:
        users = []
    return render_template('search_users.html', users=users, query=query)

@main.route('/send_friend_request/<int:user_id>', methods=['POST'])
@login_required
def send_friend_request(user_id):
    user_to_add = User.query.get_or_404(user_id)
    if user_to_add == current_user:
        flash('No puedes enviarte una solicitud de amistad a ti mismo.', 'info')
        return redirect(url_for('main.dashboard'))
    
    # Verificar si el usuario ya es un contacto
    if user_to_add in current_user.contacts.all():
        flash(f'{user_to_add.username} ya es uno de tus contactos.', 'info')
        return redirect(url_for('main.dashboard'))
    
    # Verificar si ya existe una solicitud pendiente
    existing_request = FriendRequest.query.filter_by(
        sender_id=current_user.id,
        receiver_id=user_to_add.id,
        status='pending'
    ).first()
    if existing_request:
        flash('Ya has enviado una solicitud de amistad a este usuario.', 'info')
        return redirect(url_for('main.dashboard'))
    
    # Crear nueva solicitud
    new_request = FriendRequest(sender_id=current_user.id, receiver_id=user_to_add.id)
    db.session.add(new_request)
    db.session.commit()
    flash(f'Solicitud de amistad enviada a {user_to_add.username}.', 'success')
    return redirect(url_for('main.dashboard'))


@main.route('/accept_friend_request/<int:request_id>', methods=['POST'])
@login_required
def accept_friend_request(request_id):
    # Obtener la solicitud por su ID
    friend_request = FriendRequest.query.get_or_404(request_id)
    
    # Verificar si el usuario actual es el receptor de la solicitud
    if friend_request.receiver != current_user:
        flash('No tienes permiso para aceptar esta solicitud.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    # Aceptar la solicitud
    friend_request.status = 'accepted'
    
    # Agregar al remitente como contacto del receptor y viceversa
    current_user.contacts.append(friend_request.sender)
    friend_request.sender.contacts.append(current_user)
    
    # Eliminar la solicitud de la base de datos (opcional)
    db.session.delete(friend_request)
    
    # Confirmar los cambios
    db.session.commit()
    
    flash(f'Ahora eres amigo de {friend_request.sender.username}.', 'success')
    return redirect(url_for('main.dashboard'))


@main.route('/reject_friend_request/<int:request_id>', methods=['POST'])
@login_required
def reject_friend_request(request_id):
    friend_request = FriendRequest.query.get_or_404(request_id)
    if friend_request.receiver != current_user:
        flash('No tienes permiso para rechazar esta solicitud.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    # Rechazar la solicitud
    friend_request.status = 'rejected'

    db.session.delete(friend_request)

    db.session.commit()
    flash(f'Solicitud de amistad rechazada.', 'info')
    return redirect(url_for('main.dashboard'))

@main.route('/private_chat/<int:user_id>', methods=['GET', 'POST'])
@login_required
def private_chat(user_id):
    # Obtener el usuario con quien se está chateando
    other_user = User.query.get_or_404(user_id)
    
    # Verificar si el usuario está en los contactos del usuario actual
    if other_user not in current_user.contacts.all():
        flash('Debes agregar a este usuario como contacto para chatear.', 'info')
        return redirect(url_for('main.dashboard'))
    
    # Obtener todos los mensajes entre los dos usuarios
    messages = PrivateMessage.query.filter(
        ((PrivateMessage.sender_id == current_user.id) & (PrivateMessage.receiver_id == other_user.id)) |
        ((PrivateMessage.sender_id == other_user.id) & (PrivateMessage.receiver_id == current_user.id))
    ).order_by(PrivateMessage.timestamp.asc()).all()
    
    if request.method == 'POST':
        content = request.form.get('content')
        if not content:
            flash('El mensaje no puede estar vacío.', 'danger')
        else:
            # Crear un nuevo mensaje
            new_message = PrivateMessage(
                content=content,
                sender_id=current_user.id,
                receiver_id=other_user.id
            )
            db.session.add(new_message)
            db.session.commit()
            flash('Mensaje enviado.', 'success')
            return redirect(url_for('main.private_chat', user_id=user_id))
    
    return render_template('private_chat.html', other_user=other_user, messages=messages)