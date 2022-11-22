from flask import Flask, request, render_template
import subprocess

app = Flask(__name__)

@app.route('/', methods = ["GET", "POST"])
def index():
    if request.method == 'POST':
        
        f = open("test.sh", "w")
        # f.write(request.form.get("AccessKeyID"))
        # f.write(request.form.get("SecretAccessKey"))
        f.write('''#!/bin/bash
( cd ../terraform && terraform init )''')
        f.close()
        subprocess.call(['sh', './test.sh'])
    return render_template('index.html', form=request.form, st="? (Recarregue a página para saber)")

if __name__ == "__main__":
    app.run(
        # host="169.254.0.13",
        host="localhost",
        port="8081",
        debug=False
    )