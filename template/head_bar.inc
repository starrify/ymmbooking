<div id="notification" class="modal hide fade" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true">
  		<div class="modal-header">
   		<button type="button" class="close" data-dismiss="modal" aria-hidden="true">×</button>
    	<h3 id="H2">未读消息</h3>
 		</div>
  		<div class="modal-body">
        <!--正体-->
        <div id="unread">
        </div>
        <div class="progress progress-striped active" id="Div1" style="display:none">
  			<div class="bar" style="width: 40%;"></div>
		</div>
  		</div>

</div>

<div class="navbar navbar-inverse navbar-fixed-top">
    <div class="navbar-inner">
        <div class="container-fluid">
            
            <a class="brand" href="#">Online Payment</a>
          <div class="nav-collapse collapse">
            <p class="navbar-text pull-right">
              Logged in as <a href="#Login"  data-toggle="modal" class="navbar-link" id="Username">Username</a>

                </p>
                <ul class="nav">
                    <li><a href="#">账户设置</a></li>
                    <li><a href="order_manage.html">我是买家</a></li>
                    <li><a href="#contact">我是卖家</a></li>
                    <li><a href="#contact">淘宝贝</a></li>
                    <li class="active"><a href="/">在线预订</a></li>
                    <li><a data-toggle="modal" href="#notification" id="notify" onclick="viewNotification()">消息:0</a></li>

                </ul>
            </div><!--/.nav-collapse -->
        </div>
    </div>
</div>
      <!-- 登出对话框 -->
   <div id="LoginOut" class="modal hide fade" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true">
       <div class="modal-header">
         <button type="button" class="close" data-dismiss="modal" aria-hidden="true">×</button>
         <h4 id="H1">用户登出</h4>
         <h4 href="/manage/hotel/info">|管理员</h4>
       </div>
       <div class="modal-body">
          <p>是否确定登出？</p>
       </div>
       <div class="modal-footer">
          <button class="btn btn-primary loginout"data-dismiss="modal" aria-hidden="true">登出</button>
         <button class="btn" data-dismiss="modal" aria-hidden="true">取消</button>
       </div>
  </div>

<div class="toppic">
    <img src="/img/logo1.jpg" width="100%">
    </img>
</div>
<script type="text/javascript" src="/js/jquery.js"></script>
<script type="text/javascript">
		var buid;//全局变量
		buid = getCookie("uid");
		function getCookie(objName) {
		    var arrStr = document.cookie.split(";");
		    for (var i = 0; i < arrStr.length; i++) {
		        var temp = arrStr[i].split("=");
		        if (temp[0] == objName) return unescape(temp[1]);
		    }
		}
		console.log(buid);
		function notification() {
		    var url = "../../../api/General/Notification";
		    $.ajax({
		        url: url,
		        type: "post",
		        data: { "uid": buid },
		        success: function (result) {
		            var data;
		            eval("data=" + result);
		            var num = data.NotificationNum;

		            console.log("num:" + num);
		            var node = document.getElementById("notify");
		            node.disabled
		            node.innerHTML = "消息:" + num;
		            node.style.display = "inherit";
		        }
		    })
		}
		var set = setInterval("notification()", 10000);
		$(document).ready(function (e) {
		    //获取个人信息buid


		    if (buid == null) {
		        //没有uid时需要登陆
		        var loginurl = "../index.html";
//		        window.location = loginurl;//跳转到登陆页面
		    }
		    else {
		        var username = getCookie(" username");
		        var usernamenode = document.getElementById("Username");
		        usernamenode.innerHTML = username;
		        usernamenode.setAttribute('href', '#LoginOut');
		    }
		    $(".loginout").click(function () {
		        //获取输入的密码
		        deleteCookie("username");
		        deleteCookie("uid");
		        var usernamenode = document.getElementById("Username");
		        usernamenode.innerHTML = "Username";
		        usernamenode.setAttribute('href', '#Login');
		        buid = null;
//		        window.location = "../login.html";
		    })

		    function deleteCookie(objName) {
		        var date = new Date();
		        date.setTime(date.getTime() - 10000);
		        document.cookie = objName + "=a; path=/; expires=" + date.toGMTString();

		    }
		    beginorder = 0;
		    notification();
		})

		function viewNotification() {
		    var url = "../../../api/General/ViewNotification";
		    //var url = "./2.txt";
		    var uid = buid;
		    var TEMPL = "<h5>*date</h5><p>*message</p>"
		    $.ajax({
		        url: url,
		        type: "post",
		        data: { "uid": uid },
		        success: function (result) {
		            var node = document.getElementById('notify');
		            node.innerHTML = "消息:0";
		            console.log(result);
		            var data;
		            eval("data=" + result);
		            var notis = data.Notis;
		            //	var node=document.getElementById('unread');
		            var newhtml = "";
		            for (var i = 0; i < notis.length; i++) {
		                var newmessage = TEMPL.replace(/\*date/, notis[i].GeneratedTime);
		                newmessage = newmessage.replace(/\*message/, notis[i].Message);
		                newhtml += newmessage;
		            }
		            $("#unread").html(newhtml);
		        }

		    })
		}




</script>