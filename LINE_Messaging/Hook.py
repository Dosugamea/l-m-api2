import inspect,traceback
from functools import wraps

class EventProcessor(object):
    def __init__(self,cl):
        self.cl = cl
        self.efuncs = []
    def e_do(self,data):
        for e in data["events"]:
            for func in self.efuncs:
                try:
                    if func(self,e): break
                except Exception as e:
                    print(traceback.format_exc())
class MessageProcessor(object):
    def __init__(self,cl):
        self.cl = cl
        self.mfuncs = []
    def m_do(self,msg):
        for func in self.mfuncs:
            try:
                if func(self,msg): break
            except Exception as e:
                print(traceback.format_exc())
class CommandProcessor(object):
    def __init__(self,cl):
        self.cl = cl
        self.cfuncs = []
    def c_do(self,msg):
        self.msg = msg
        for func in self.cfuncs:
            try:
                if func(self,msg): break
            except Exception as e:
                print(traceback.format_exc())
    # List help (Not useful, needs fix.)
    def help(self,list=False,hidden=[],noprefix=[]):
        ls = [[x.__name__,x.__doc__] for x in self.cfuncs if x.__name__ not in hidden]
        ls = [l for l in ls if l[1] != None]
        if list: return ls
        else: return "[Command List]\n"+"\n".join([self.prefix+l[0]+" : "+l[1] if l[0] not in noprefix else l[0]+" : "+l[1] for l in ls])
    # Message Checker
    def process(self,users,groups,permissions):
        pcheck,execute = False,False
        msg = self.msg
        #From Group
        if msg["source"]["type"] == "group":
            # If group is not denied
            if groups not in [[None],[]]:
                # If accept from ALL or gid in groups
                if ("ALL" in groups or msg["source"]["groupId"] in groups): pcheck = True
                # If group type name registered
                elif groups[0] in self.groups: 
                    if [g for g in groups if msg["source"]["groupId"] in self.groups[g]] != []: pcheck = True
                # Else ( doesn't happen defaultly)
                else: raise ValueError("[Cmd][%s] Invalid groups paramator"%(func.__name__))
        #From 1-1
        elif msg["source"]["type"] == "user":
            # If 1-1 is not denied
            if users not in [[None],[]]:
                # If accept from ALL or mid in users
                if ("ALL" in users or msg["source"]["userId"] in users): pcheck = True
                # If user type name registered
                elif users[0] in self.users:
                    if [u for u in groups if msg["source"]["userId"] in self.users[u]] != []: pcheck = True
                # Else ( doesn't happen defaultly)
                else: raise ValueError("[Cmd][%s] Invalid users paramator"%(func.__name__))
        #Do Permission Check
        if pcheck:
            if "ALL" in permissions: execute = True
            elif [p for p in permissions if msg["source"]["userId"] in self.permissions[p]] != []: execute = True
        return execute   
                
class HookExecuter(EventProcessor,MessageProcessor,CommandProcessor):
    def __init__(self,cl,users={"Active":["INPUT_MID"]},groups={"Active":["INPUT_GID"]},permissions={"ADMIN":["INPUT_YOUR_MID"]},prefix=".",datas=None):
        EventProcessor.__init__(self,cl)
        MessageProcessor.__init__(self,cl)
        CommandProcessor.__init__(self,cl)
        self.prefix = prefix
        self.users  = users
        self.groups = groups
        self.permissions = permissions
        self.datas = datas
    # Execute(Main)
    def trace(self,data,type="Event"):
        if type == "Event": self.e_do(data)
        elif type == "Message": self.m_do(data)
        elif type == "Command": self.c_do(data)
        else: raise TypeError("Trace type parameter is invalid")
    # Make log
    def log(self,text):
        print("[{}] {}".format(str(datetime.now()), text))
    # Register a func to Commander / Runner
    def addFunc(self,func,type="Events"):
        if type in ["Events",0]: self.efuncs.append(func)
        elif type in ["Messages",1]: self.mfuncs.append(func)
        elif type in ["Commands",2]: self.cfuncs.append(func)
        else: raise TypeError("Func type parameter is invalid")
    # Register funcs in a class to Commander / Runner
    def addClass(self,_class,type="Events"):
        if type in ["Events",0]:
            for func in [x[1] for x in inspect.getmembers(_class, predicate=inspect.ismethod)]:
                self.efuncs.append(func)
        elif type in ["Messages",1]:
            for func in [x[1] for x in inspect.getmembers(_class, predicate=inspect.ismethod)]:
                self.mfuncs.append(func)
        elif type in ["Commands",2]:
            for func in [x[1] for x in inspect.getmembers(_class, predicate=inspect.ismethod)]:
                self.cfuncs.append(func)
        else:
            raise TypeError("Class type parameter is invalid")
    # Last crazy solution. use only if can't solve by safe way.
    def makeGlobal(self,names):
        for n in names:
            exec("global %s"%(n))

# EventChecker (Check EventType)
def Event(opType):
    def __wrapper(func):
        @wraps(func)
        def __check(self, *args, **kwargs):
            if args[1]["type"] == opType:
                try:
                    func(args[0],args[1])
                    return True
                except:
                    print(traceback.format_exc())
        return __check
    return __wrapper

# MessageChecker (Check MessageType)
def Message(contentType):
    def __wrapper(func):
        @wraps(func)
        def __check(self, *args, **kwargs):
            if args[1]['message']['type'] == contentType:
                try:
                    func(args[0],args[1])
                    return True
                except:
                    print(traceback.format_exc())
        return __check
    return __wrapper
    
# CommandChecker (Check Commands)
def Command(alt=[],users=["ALL"],groups=["ALL"],permissions=["ALL"],inpart=False,prefix=True,convert_lower=False):
    def __wrapper(func):
        @wraps(func)
        def __check(self, *args, **kwargs):
            scheck,pcheck,execute = False,False,False
            msg = args[1]["message"]
            # Use prefix or not
            if prefix:
                prefi = args[0].prefix
            else:
                prefi = ""
            # Convert to lowercase or not
            if convert_lower: msg["text"] = msg["text"].lower()
            # Check a part match
            if inpart:
                if any([msg["text"].startswith(x) for x in [prefi+c for c in alt+[func.__name__]]]):
                    scheck = True
            # Check a perfect match
            else:
                if msg["text"] in [prefi+c for c in alt+[func.__name__]]:
                    scheck = True
            # Check permissions
            if scheck:
                execute = args[0].process(users,groups,permissions)
            # Do it if checks are all ok
            if execute:
                try:
                    func(args[0],msg)
                    return True
                except:
                    print(traceback.format_exc())
        return __check
    return __wrapper