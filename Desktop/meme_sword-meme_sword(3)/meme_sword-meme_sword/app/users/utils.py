import os
from threading import Thread
from flask_mail import Message
from app import app
from flask import render_template
from app import mail
from PIL import Image, ImageSequence

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(subject,sender,recipents,text_body,html_body):
    msg=Message(subject,sender=sender,recipients=recipents)
    msg.body=text_body
    msg.html=html_body
    Thread(target=send_async_email,args=(app,msg)).start()

def send_password_reset_email(user):
    token=user.get_reset_password_token()
    send_email("M3M3SWORD Reset Password",sender=os.environ.get("MAIL_USERNAME"),
               recipents=[user.email],text_body=render_template("email/reset_password.txt",user=user,token=token),
               html_body=render_template("email/reset_password.html",user=user,token=token))

def resize_gif(input_path, output_path, new_width, new_height):
    # Open the GIF file
    with Image.open(input_path) as img:
        # Initialize a list to store resized frames
        resized_frames = []

        for frame in ImageSequence.Iterator(img):
            # Resize each frame
            resized_frame = frame.resize((new_width, new_height), Image.ANTIALIAS)
            resized_frames.append(resized_frame)

        # Save the resized frames as a new GIF
        resized_frames[0].save(
            output_path,
            save_all=True,
            append_images=resized_frames[1:],
            loop=0,
            duration=img.info['duration']
        )
