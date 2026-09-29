import re

from flask import Flask, render_template, session, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, SubmitField
from wtforms.validators import DataRequired, Email

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'

bootstrap = Bootstrap(app)
moment = Moment(app)


class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    email = EmailField('What is your UofT Email address?', validators=[DataRequired(), Email()])
    submit = SubmitField('Submit')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


def is_uoft_email(email):
    return email is not None and 'utoronto' in email.lower()


@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        old_name = session.get('name')
        if old_name is not None and old_name != form.name.data:
            flash('Looks like you have changed your name!')
        old_email = session.get('email')
        if old_email is not None and old_email != form.email.data:
            flash('Looks like you have changed your email!')
        session['name'] = form.name.data
        session['email'] = form.email.data
        # A name plus a valid UofT email unlocks the chatbot page
        if is_uoft_email(form.email.data):
            return redirect(url_for('chatbot'))
        return redirect(url_for('index'))
    email = session.get('email')
    return render_template('index.html', form=form, name=session.get('name'),
                           email=email, is_uoft=is_uoft_email(email))


@app.route('/chatbot')
def chatbot():
    # Only users who submitted a name and a UofT email may open the chat page
    if not session.get('name') or not is_uoft_email(session.get('email')):
        return redirect(url_for('index'))
    return render_template('chat.html', name=session['name'])


MY_NAME_IS = re.compile(r"\bmy name is\s+(.+)", re.IGNORECASE)


@app.route("/chat", methods=["POST"])
def chat():
    message = request.json["message"]
    lower = message.lower()

    match = MY_NAME_IS.search(message)
    told_name = match.group(1).strip().rstrip(".!?").strip() if match else ""

    if told_name:
        # Remember the name in the session so that later requests can use it
        session["chat_name"] = told_name
        reply = f"Nice to meet you, {told_name}!"
    elif "what is my name" in lower or "what's my name" in lower:
        chat_name = session.get("chat_name")
        if chat_name:
            reply = f"Your name is {chat_name}."
        else:
            reply = "I don't know your name yet. Tell me by saying \"My name is ...\"."
    elif "hello" in lower:
        reply = "Hello!"
    else:
        reply = "I don't understand."

    return {"reply": reply}


@app.route('/logout', methods=['POST'])
def logout():
    # Forget everything stored for this browser: name, email and the chatbot memory
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('index'))


@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)


if __name__ == '__main__':
    app.run(debug=True)
