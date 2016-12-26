from flask import Flask, request, render_template, url_for, redirect
import re
import sqlite3
import random
import string

app = Flask(__name__, static_url_path='')

def generateRandom():
	return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(8))


def strip_script_tags(content):
    pattern = re.compile(r'\s?on\w+="[^"]+"\s?')
    result = re.sub(pattern, "", content) 
    pattern2 = re.compile(r'<script[\s\S]+?/script>')
    result = re.sub(pattern2, "", result)
    return result


@app.route('/new', methods=['POST'])
def new():
	if request.method == 'POST':

		content = strip_script_tags(request.form['content']).replace("'", "\"")
		title = re.sub('<[^<]+?>', '', request.form['title']).replace("'", "\"")
		url = request.form['url']
		pid = generateRandom()

		conn = sqlite3.connect('pages.db')
		c = conn.cursor()

		c.execute('INSERT OR IGNORE INTO pages (id, title, url, content) VALUES (\'%s\', \'%s\', \'%s\', \'%s\')' % (pid, title, url, content))
		conn.commit()

		c.close()

		return '{ "pid":"'+pid+'" }'
	else:
		return '{ "error":"invalid request" }'

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/p/<pid>')
def page(pid=None):
	if pid == None:
		return render_template('index.html')
	else:
		conn = sqlite3.connect('pages.db')
		c = conn.cursor()
		c.execute('SELECT * FROM pages WHERE id="'+pid+'"')
		result = c.fetchone()
		if result != None:
			if result[2] != '':
				scripts = '<script type="text/javascript">setInterval(function(){ window.location.replace("'+result[2]+'") }, 1000);</script>'
				return render_template('page.html', title=result[1], scripts=scripts, content=result[3])
			else:
				return render_template('page.html', title=result[1], content=result[3])
		else:
			return render_template('index.html')
		


if __name__ == '__main__':
	app.run(host='0.0.0.0', port=80, debug=True)