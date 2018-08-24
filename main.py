from bottle import route,run,response,request,static_file
from LINE_Messaging import LINE,HookExecuter,Event,Message,Command

class Events(object):
    @Event("message")
    def got_message(self,msg):
        self.cl.setReplyToken(msg["replyToken"])
        self.trace(msg,type="Message")
    @Event("follow")
    def got_follow(self,msg):
        print("FOLLOW")
        self.cl.setReplyToken(msg["replyToken"])
        self.cl.addMessage("Thanks for add me!")
        self.cl.replyMessage()
    @Event("unfollow")
    def got_unfollow(self,msg):
        print("UNFOLLOW")
        #self.cl.setReplyToken(msg["replyToken"])
        #self.cl.addMessage("Why you unfollow me!!!!!!!")
        #self.cl.replyMessage()
    @Event("join")
    def got_join(self,msg):
        print("JOIN")
        self.cl.setReplyToken(msg["replyToken"])
        self.cl.addMessage("Thanks for invite me to this group!")
        self.cl.replyMessage()
    @Event("leave")
    def got_leave(self,msg):
        print("LEAVE")
        print(msg)
    @Event("postback")
    def got_postback(self,msg):
        print("POSTBACK")
        self.cl.setReplyToken(msg["replyToken"])
        print(msg)
        
class Messages(object):
    @Message("text")
    def got_text(self,msg):
        print(msg)
        self.trace(msg,type="Command")
    @Message("image")
    def got_image(self,msg):
        print(msg)
        self.cl.addMessage("Kawaii!")
        self.cl.replyMessage()
    @Message("video")
    def got_video(self,msg):
        print(msg)
        self.cl.addMessage("Nice Video!")
        self.cl.replyMessage()
    @Message("audio")
    def got_audio(self,msg):
        print(msg)
        self.cl.addMessage("Nice audio!")
        self.cl.replyMessage()
    @Message("file")
    def got_file(self,msg):
        print(msg)
        self.cl.addMessage("I can't see the file!")
        self.cl.replyMessage()
    @Message("location")
    def got_location(self,msg):
        print(msg)
        self.cl.addMessage("Oh, you are at there?")
        self.cl.replyMessage()
    @Message("sticker")
    def got_sticker(self,msg):
        print(msg)
        cl.addSticker(self,1,2)
        cl.replyMessage()

class Commands(object):
    @Command(alt=["ハロー","hello"],users=["ALL"])
    def hi(self,msg):
        '''Check the bot Alive'''
        print(msg)
        self.cl.addMessage("Hi too!")
        self.cl.replyMessage()
    @Command(users=["ALL"])
    def help(self,msg):
        '''Display this help message'''
        self.cl.addMessage(self.help())
        self.cl.replyMessage()

cl = LINE(channelAccessToken="TOKEN")
tracer = HookExecuter(cl,prefix="!")
tracer.addClass(Events(),type="Events")
tracer.addClass(Messages(),type="Messages")
tracer.addClass(Commands(),type="Commands")

@route('/callback',method='POST')
def bot():
    data = request.json
    tracer.trace(data)
    return "OK"
 
if __name__ == "__main__":
    run(host="localhost", port=8080,reload=False)