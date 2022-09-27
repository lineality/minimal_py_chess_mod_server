# Import Packages & Libraries
from flask import Flask, jsonify, request, render_template
import gunicorn

# Required for Flask/Heroku
app = Flask(__name__)

## art for home page
home_page = """<html>
    <body>
      <body style="background-color:black;">
      <font color="00FF00">  
            <div style="line-height:1px">
        <tt> 
<p style="font-size:40px; "> r n b q k b n r </p>
<p style="font-size:40px; "> p p p p p p p p </p>
<p style="font-size:40px; "> . . . . . . . . </p>
<p style="font-size:40px; "> . . . . . . . . </p>
<p style="font-size:40px; "> . . . P . . . . </p>
<p style="font-size:40px; "> . . . . . . . . </p>
<p style="font-size:40px; "> P P P . P P P P </p>
<p style="font-size:40px; "> R N B Q K B N R </p>
<p style="font-size:20px; "> 鰻　み　岡　野　エ　た　ラ　お　天　白 </p>
<p style="font-size:20px; "> 丼　そ　山　菜　ビ　こ　ー　で　丼　竜 </p>
<p style="font-size:20px; "> 八　カ　の　天　フ　焼　メ　ん　八　 </p>
<p style="font-size:20px; "> 三　ツ　ラ　ぷ　ラ　き　ン　四　円 </p>
<p style="font-size:20px; "> 百　ラ　ー　ら　イ　三　二　円 </p>
<p style="font-size:20px; "> 六　ー　メ　八　十　円 </p>
<p style="font-size:20px; "> 十　メ　ン　五　円 </p>
<p style="font-size:20px; "> 三　ン　十　円 </p>
<p style="font-size:20px; "> 八　万　円 </p>
<p style="font-size:20px; "> 万　円 </p>
<p style="font-size:20px; "> 円　</p>
      </div>
    </body>
</html>
"""

whitelist_dictionary_ip_game = {
"tyrell": "avalon_2601:81:102:1280::92ce,2601:81:102:1280,pawpaw_data_174:247:80:180, 28th_76.116.21.34",
"trident":"",
}

# helper function
def get_user_ip():
    """
    Flask app get ip of user.
    """
    if request.headers.getlist("X-Forwarded-For"):
        user_ip = request.headers.getlist("X-Forwarded-For")[0]
        print("\nuser ip from proxy port forwarding list\n")

    else:
        user_ip = request.remote_addr
        # Terminal Print
        print("\nNormal IP, no proxy or forwarding.\n")

    user_ip = str(user_ip)
    user_ip = user_ip.replace(' ','')

    print(f"user user_ip:\n'{user_ip}'", )

    return user_ip

# helper function
def check_ip_whitelist(game_name, user_ip):
    """
    Also requires another helper function and lookup dict (or other lookup): 
        - get_user_ip()
        - whitelist_dictionary_ip_game = {}
        
    Example Use:
    
    # set inputs:
    game_name = "tyrell"
    the_user_is = get_user_ip()
    
    # run the check:
    boolean_ip_whitelist_check = check_ip_whitelist( game_name, the_user_is)
    
    print(boolean_ip_whitelist_check)
    """
    
    output = False

    try:
        if user_ip in whitelist_dictionary_ip_game[game_name]:
            output = True

    except:
        # default to false, if for whatever reason check does not work
        pass

    return output

# Your Home Screen
@app.route('/')
def home():

    print(f"user user_ip:\n'{get_user_ip()}'", )

    game_name = "tyrell"
    the_user_is = get_user_ip()
    boolean_ip_whitelist_check = check_ip_whitelist( game_name, the_user_is)
    print(boolean_ip_whitelist_check)

    return home_page

if __name__ == "__main__":
    app.run_server
