import datetime

class user_status :
  user_list = {}

  def __init__(self) :
    self.user_list = {}
    self.login_user("mmchang76@gmail.com", [127, 60])

  def fake_user(self) :
    self.login_user("cjchoi", [25,30])
    self.login_user("kpop", [20,40])
    self.login_user("ghost", [200,300])
    self.login_user("cup", [12, 22])
    self.login_user("bird", [62, 52])
    self.login_user("girl", [30, 32])

  def login_user(self, auser, apoint = [0,0]) :
    # hash map? or list ?, 
    # key is auser, they have a current point, time, login status
    v = { auser : [ apoint, datetime.datetime.utcnow(), 1 ] }
    self.user_list.update(v)

  def update_user(self, auser, apoint) :
    login_time = self.user_list[auser][1]
    v = { auser : [ apoint, login_time, 1 ] }
    self.user_list.update(v)
 
  def logout_user(self, auser) :
    last_point = self.user_list[auser][0] 
    #login_time = self.user_list[auser][1]
    # log out time
    login_time = datetime.datetime.utcnow()
    v = { auser : [ last_point, login_time, 0 ] }
    self.user_list.update(v)

  def clear_user(self) :
    self.user_list = {}

  """ Highly optimized code we need """
  def find_near(self, auser) :
    # return list
    near_user_list = []
    # manathon distance first 
    last_point = self.user_list[auser][0]
    lpx = last_point[0]
    lpy = last_point[1]
    for k, v in self.user_list.items() :
      if (k == auser) : continue
      px = v[0][0]
      py = v[0][1]   
      dist = abs(lpx - px) + abs(lpy - py)
      if ( dist < 100 ) :
        near_user_list.append(k)
    return near_user_list

  def pt(self) :
    print self.user_list

# It's Test Code 
def main() :
  u = user_status()
  u.login_user("cjchoi", [10,20])
  u.pt()
  u.update_user("cjchoi", [10,30])
  u.pt()
  u.login_user("kpop", [20,40])
  u.login_user("ghost", [200,300])
  u.login_user("bythepeople", [12, 22])
  print u.find_near("cjchoi")

if __name__ == '__main__' :
  main()

