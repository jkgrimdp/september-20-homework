import psycopg2
from flask import Flask, request, jsonify

app = Flask(__name__)

conn = psycopg2.connect("dbname='usermgt' user='jacobgrimshaw' host='localhost'" )
cursor = conn.cursor()

def create_all():
   print("Creating tables...")
   cursor.execute("""
      CREATE TABLE IF NOT EXISTS Users (
         user_id SERIAL PRIMARY KEY,
         first_name VARCHAR NOT NULL,
         last_name VARCHAR,
         email VARCHAR NOT NULL UNIQUE,
         phone VARCHAR,
         city VARCHAR,
         state VARCHAR,
         org_id int,
         active smallint
      );
   """)
   cursor.execute("""
      CREATE TABLE IF NOT EXISTS Organizations (
         org_id SERIAL PRIMARY KEY,
         name VARCHAR NOT NULL,
         phone VARCHAR,
         city VARCHAR,
         state VARCHAR,
         active smallint
      );
   """)
   conn.commit()

# ADD/CREATE

def add_org(name, phone, city, state, active):
  cursor.execute("""
    INSERT INTO organizations
    (name, phone, city, state, active)
    VALUES
    (%s, %s, %s, %s, %s);""",
  (name, phone, city, state, active))

  conn.commit()

@app.route('/org/add', methods=['POST'])
def add_org_route():
  data = request.form if request.form else request.json
  
  name = data.get('name')
  phone = data.get('phone')
  city = data.get('city')
  state = data.get('state')
  active = data.get('active')
  
  add_org(name, phone, city, state, active)

  return jsonify("Org Created"), 200

def add_user(first_name, last_name, email, phone, city, state, org_id, active):
  cursor.execute(f"""
    INSERT INTO users 
      (first_name, last_name, email, phone, city, state, org_id, active)
      VALUES 
      (%s, %s, %s, %s, %s, %s, %s, %s);""",
    (first_name, last_name, email, phone, city, state, org_id, active))

  conn.commit()

@app.route('/user/add', methods=['POST'])
def user_add():
  post_data = request.form
  first_name = post_data.get('first_name')
  last_name = post_data.get('last_name')
  email = post_data.get('email')
  phone = post_data.get('phone')
  city = post_data.get('city')
  state = post_data.get('state')
  org_id = post_data.get('org_id')
  active = post_data.get('active')

  add_user(first_name, last_name, email, phone, city, state, org_id, active)

  return jsonify("User created"), 201

# UPDATE

@app.route('/user/update/<user_id>', methods=['POST', 'PUT'])
def user_update(user_id):
  update_fields = []
  update_values = []
  field_names = ['first_name', 'last_name', 'email', 'phone', 'city', 'state', 'org_id', 'active']

  post_data = request.json

  for field in field_names:
    field_value = post_data.get(field)
    if field_value:
      update_fields.append(str(field) + '=%s')
      update_values.append(field_value)

  if update_fields:
    update_values.append(user_id)
    query_string = f"UPDATE users SET " + ', '.join(update_fields) + " WHERE user_id=%s"
    cursor.execute(query_string, update_values)
    conn.commit()

    return jsonify("User Updated"), 200
  else:
    return jsonify("No values sent in body"), 418

@app.route('/org/update/<org_id>', methods=['POST', 'PUT'])
def org_update(org_id):
  update_fields = []
  update_values = []
  field_names = [('name', 'phone', 'city', 'state', 'active')]

  post_data = request.json

  for field in field_names:
    field_value = post_data.get(field)
    if field_value:
      update_fields.append(str(field) + '=%s')
      update_values.append(field_value)

  if update_fields:
    update_values.append(user_id)
    query_string = f"UPDATE organizations SET " + ', '.join(update_fields) + " WHERE org_id=%s"
    cursor.execute(query_string, update_values)
    conn.commit()

    return jsonify("Org Updated"), 200
  else:
    return jsonify("No values sent in body"), 418

# GET BY ID

@app.route('/user/<user_id>')
def get_user_by_id(user_id):
  cursor.execute("""
    SELECT * FROM users
      WHERE user_id=%s;""",
    [user_id])
  results = cursor.fetchone()
  organization = get_org_by_id(results[7])
  # return organization

  if results:

    user = {
      'user_id':results[0], 
      'first_name':results[1], 
      'last_name':results[2], 
      'email':results[3], 
      'phone':results[4], 
      'city':results[5], 
      'state':results[6], 
      'organization':organization,
      # 'org_id':results[7],  
      'active':results[8]
    }
    return jsonify(user), 200

  else:
    return jsonify('User Not Found'), 404

@app.route('/org/<org_id>')
def get_org_by_id(org_id):
  cursor.execute("""
    SELECT * FROM organizations
      WHERE org_id=%s;""",
    [org_id])
  results = cursor.fetchone()
  if results:
    org = {
      'org_id':results[0],
      'name':results[1],
      'phone':results[2],
      'city':results[3],
      'state':results[4],
      'active':results[5]
    }
    return (org)
  else:
    return jsonify('Organization Not Found'), 404

# GET ALL

@app.route('/users/get', methods=['GET'])
def get_all_active_users():
  cursor.execute("""
  SELECT * FROM users
    WHERE active=1;""")
  results = cursor.fetchall()
  if results:
    users = []
    for result in results:
      user_record = {
        'user_id':result[0], 
        'first_name':result[1], 
        'last_name':result[2], 
        'email':result[3], 
        'phone':result[4], 
        'city':result[5], 
        'state':result[6], 
        'org_id':result[7], 
        'active':result[8]
      }
      users.append(user_record)

    return jsonify(users), 200
  else:
    return jsonify('Users Not Found'), 404

@app.route('/orgs/get', methods=['GET'])
def get_all_active_orgs():
  cursor.execute("""
  SELECT * FROM organizations
    WHERE active=1;""")
  results = cursor.fetchall()
  if results:
    orgs = []
    for result in results:
      org_record = {
        'org_id':result[0],
        'name':result[1],
        'phone':result[2],
        'city':result[3],
        'state':result[4],
        'active':result[5]
      }
      orgs.append(org_record)

    return jsonify(orgs), 200
  else:
    return jsonify('Oranizations Not Found'), 404

# ACTIVATE

@app.route('/user/activate/<user_id>')
def activate_user(user_id):
  cursor.execute("""
    UPDATE users
      SET active=1
      WHERE user_id=%s;""",
      [user_id])
  conn.commit()
  return jsonify("User activated"), 200

@app.route('/org/activate/<org_id>')
def activate_org(org_id):
  cursor.execute("""
    UPDATE organizations
      SET active=1
      WHERE org_id=%s;""",
      [org_id])
  conn.commit()
  return jsonify("org activated"), 200

# DEACTIVATE
 
@app.route('/user/deactivate/<user_id>')
def deactivate_user(user_id):
  cursor.execute("""
    UPDATE users
      SET active=0
      WHERE user_id=%s;""",
      [user_id])
  conn.commit()
  return jsonify("User deactivated"), 200
 
@app.route('/org/deactivate/<org_id>')
def deactivate_org(org_id):
  cursor.execute("""
    UPDATE organizations
      SET active=0
      WHERE org_id=%s;""",
      [org_id])
  conn.commit()
  return jsonify("Organization deactivated"), 200

# DELETE

@app.route('/user/delete/<user_id>')
def delete_user(user_id):
  cursor.execute("""
  DELETE FROM users WHERE user_id=%s;""",
  [user_id])
  conn.commit()
  return jsonify("User deleted")

@app.route('/org/delete/<user_id>')
def delete_org(org_id):
  cursor.execute("""
  DELETE FROM organizations WHERE org_id=%s;""",
  [org_id])
  conn.commit()
  return jsonify("Organization deleted")

# add_user("Andrew", "Grimshaw", "andrew@devpipeline.com", "1233455678", "Mapleton", "UT", None, 0)
# user = get_user_by_id(3)
# print(user)
# actives = get_all_active_users()
# print(actives)

if __name__ == '__main__':
  create_all()
  app.run(host='0.0.0.0', port=8086)