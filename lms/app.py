from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, \
    current_user, login_user, logout_user, login_required
from lms.config import Config

app = Flask(__name__)
app.config['SECRET_KEY'] = 'you-will-never-guess'
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
loginManager = LoginManager(app)

#pylint: disable=wrong-import-position
from lms.utils import blank_resp, init_user, init_student, get_response
from lms.forms import RegForm, PreliminaryRegForm, PreliminaryStudentRegForm, \
    LoginForm, CourseForm, PersonalInfoForm, GroupForm, ScheduleForm
from lms.Domain.Users import User
from lms.Domain.Courses import Course, Schedule
from lms.Domain.Students import Student, Group
from lms.Domain.Teachers import Teacher
#pylint: enable=wrong-import-position

def add_course_in(form):
    course = Course(name=form.name.data, description=form.description.data)
    db.session.add(course)
    db.session.commit()


def add_group_in(form):
    group = Group(name=form.name.data, department=form.department.data)
    db.session.add(group)
    db.session.commit()


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/preliminary_register', methods=['POST'])
@login_required
def preliminary_register_user():
    """Администратор может добавить предопределенного пользователя (студента или преподавателя)

    """
    answer = blank_resp()

    try:
        if current_user.status != 'admin':
            raise Exception('Only admins can do preliminary registration')
        form = PreliminaryRegForm(request.form)
        if form.validate():
            user = init_user(form)

            db.session.add(user)
            db.session.commit()

            if user.get_status() == 'student':
                form_student = PreliminaryStudentRegForm(request.form)
                if form_student.validate():
                    user_id = user.get_user_id()
                    group = Group.query.filter_by(name=form_student.group.data).first()
                    if group is None:
                        raise Exception('This group doesn\'t exist. Please, firstly, create group.')
                    group_id = group.get_id()
                    student = init_student(form_student, user_id, group_id)
                    db.session.add(student)
                    db.session.commit()
                else:
                    db.session.delete(user)
                    db.session.commit()
                    raise Exception(str(form_student.errors.items()))
            answer['data'] = str({'validation_code': user.get_registration_uid()})
        else:
            raise Exception(str(form.errors.items()))

    except Exception as exception:
        answer['status'] = 'error'
        answer['error_message'] = str(exception)

    return get_response(answer)


@app.route('/register', methods=['POST'])
def register_user():
    """Пользователь может зарегистрироваться в системе
    по коду регистрации, полученного от администратора.

    """
    answer = blank_resp()

    try:
        registration_uid = request.form.get('validation_code')
        user = User.query.filter_by(registration_uid=registration_uid).first_or_404()

        form = RegForm(request.form)
        if form.validate():
            user.set_username(form.username.data)
            user.set_email(form.email.data)
            user.set_password(form.password.data)

            db.session.commit()
        else:
            raise Exception(str(form.errors.items()))
    except Exception as exception:
        answer['status'] = 'error'
        answer['error_message'] = str(exception)

    return get_response(answer)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Пользователь может войти в систему по своему e-mail и паролю.

    """
    answer = blank_resp()

    try:
        if current_user.is_authenticated:
            raise Exception('User is already authenticated')
        form = LoginForm(request.form)
        if form.validate():
            user = User.query.filter_by(email=form.email.data).first()
            if user is None or not user.check_password(form.password.data):
                raise Exception('Invalid username or password')
            login_user(user)
        else:
            raise Exception(str(form.errors.items()))

    except Exception as exception:
        answer['status'] = 'error'
        answer['error_message'] = str(exception)

    return get_response(answer)


@app.route('/logout')
def logout():
    answer = blank_resp()
    try:
        logout_user()
    except Exception as exception:
        answer['status'] = 'error'
        answer['error_message'] = str(exception)

    return get_response(answer)


@app.route('/user/<username>', methods=['GET', 'POST'])
@login_required
def user(username):
    """Пользователь может просмотреть (GET) и отредактировать (POST) свой профиль.
    Помимо своего личного профиля, пользователь также может
    просматривать профили других пользователей системы.
    Однако, основу обучения видеть другие пользователи не могут.

    """
    answer = blank_resp()

    try:
        user = User.query.filter_by(username=username).first_or_404()
        if request.method == 'GET':
            if current_user.username == username:
                answer['data'] = 'full' + user.get_full_info()
            else:
                answer['data'] = str(user)
        if request.method == 'POST':
            if current_user.username != username:
                raise Exception('You can\'t edit this page')
            form = PersonalInfoForm(request.form)
            if form.validate():
                user.set_personal_info(form.phone.data, form.city.data, form.description.data)
                db.session.commit()
                answer['data'] = str(user)
            else:
                raise Exception(str(form.errors.items()))
    except Exception as exception:
        answer['status'] = 'error'
        answer['error_message'] = str(exception)

    return get_response(answer)


@app.route('/validation_code/<id>', methods=['GET'])
@login_required
def validation_code(id):
    answer = blank_resp()

    try:
        if current_user.status != 'admin':
            raise Exception('Only admins can see validation code')
        if request.method == 'GET':
            user = User.query.filter_by(id=id).first_or_404()
            answer['data'] = user.get_registration_uid()
    except Exception as exception:
        answer['status'] = 'error'
        answer['error_message'] = str(exception)

    return get_response(answer)


@app.route('/create_course', methods=['POST'])
@login_required
def create_course():
    """ Администратор может создать учебный курс, указав его название и текстовое описание.

    """
    answer = blank_resp()

    try:
        if current_user.status != 'admin':
            raise Exception('Only admins can create course')
        form = CourseForm(request.form)
        if form.validate():
            add_course_in(form)
        else:
            raise Exception(str(form.errors.items()))
    except Exception as exception:
        answer['status'] = 'error'
        answer['error_message'] = str(exception)

    return get_response(answer)


@app.route('/create_group', methods=['POST'])
@login_required
def create_group():
    """ Администратор может создать учебную группу, указав следующие данные:
        Имя группы, Имя факультета, Номер курса

    """
    answer = blank_resp()

    try:
        if current_user.status != 'admin':
            raise Exception('Only admins can create group')
        form = GroupForm(request.form)
        if form.validate():
            add_group_in(form)
        else:
            raise Exception(str(form.errors.items()))
    except Exception as exception:
        answer['status'] = 'error'
        answer['error_message'] = str(exception)

    return get_response(answer)


@app.route('/get_all', methods=['GET'])
@login_required
def get_all():
    answer = blank_resp()

    try:
        if current_user.status != 'admin':
            raise Exception('Only admins can get full information')
        type = request.args.get('type')
        if type == 'users':
            answer['data'] = str(User.query.all())
        elif type == 'courses':
            answer['data'] = str(Course.query.all())
        elif type == 'students':
            answer['data'] = str(Student.query.all())
        elif type == 'groups':
            answer['data'] = str(Group.query.all())
        else:
            raise Exception('Invalid type')
    except Exception as exception:
        answer['status'] = 'error'
        answer['error_message'] = str(exception)

    return get_response(answer)


@app.route('/get_my_classmates', methods=['GET'])
@login_required
def get_my_classmates():
    """Студент может просматривать список своих одногруппников.

    """
    answer = blank_resp()

    try:
        username = current_user.username
        user = User.query.filter_by(username=username).first()
        user_id = user.get_id()
        student = Student.query.filter_by(user_id=user_id).first()
        if student is None:
            raise Exception('You are not student')
        group_id = student.get_group_id()
        students = Student.query.filter_by(group_id=group_id).all()
        answer['data'] = str(students)
    except Exception as exception:
        answer['status'] = 'error'
        answer['error_message'] = str(exception)

    return get_response(answer)


@app.route('/add_group_to_course', methods=['POST'])
@login_required
def add_group_to_course():
    answer = blank_resp()

    try:
        if current_user.status != 'admin':
            raise Exception('Only admins can add group to course')
        form = ScheduleForm(request.form)
        if form.validate():
            group = Group.query.filter_by(name=form.group.data).first()
            if group is None:
                raise Exception('There is not such group')
            course = Course.query.filter_by(name=form.course.data).first()
            if course is None:
                raise Exception('There is not such course')
            schedule = Schedule(group_id=group.get_id(), course_id=course.get_id())
            db.session.add(schedule)
            db.session.commit()
        else:
            raise Exception(str(form.errors.items()))
    except Exception as exception:
        answer['status'] = 'error'
        answer['error_message'] = str(exception)

    return get_response(answer)


@app.route('/get_my_courses', methods=['GET'])
@login_required
def get_my_courses():
    """Пользователь может просматривать список своих курсов.

    """
    answer = blank_resp()

    try:
        username = current_user.username
        user = User.query.filter_by(username=username).first()
        user_id = user.get_id()
        student = Student.query.filter_by(user_id=user_id).first()
        if student is None:
            raise Exception('You are not student')
        group_id = student.get_group_id()
        my_schedule = Schedule.query.filter_by(group_id=group_id).all()
        answer['data'] = str(my_schedule)
    except Exception as exception:
        answer['status'] = 'error'
        answer['error_message'] = str(exception)

    return get_response(answer)


if __name__ == '__main__':
    app.run()
