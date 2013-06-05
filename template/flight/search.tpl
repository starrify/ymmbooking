<!DOCTYPE html>
<html>
  <head>
    <title>国内机票搜索</title>   
    <meta charset=utf-8>        
	<link href="/css/bootstrap.css" rel="stylesheet" type="text/css" />
    <link href="/css/style_nomal.css" rel="stylesheet" type="text/css" />
<!--what a mess code.-->
<script src="/js/jquery.js"></script>
<script>
function fetch_flight(d_city, a_city, d_date) { 
    console.log(d_city);
    $('#flight_list').html('查询中, 请稍候...')
    $.getJSON(
        "/flight/search/async",
        { 
            departure_city: d_city, 
            arrival_city:   a_city, 
            departure_date: d_date, 
        },
        function(data) {
            console.log(data)
            $('#flight_list').html('')
            for (var i in data.flight) {
                flight = data.flight[i]
                console.log(flight)
                $("#flight_list").append($("<div>", { html: flight.join(", ") }))
            }
            if (data.flight.length == 0)
                $('#flight_list').html('未查询到满足条件的航班')
        }
    );
}
</script>

  </head>
  <body>
  
  
 <div class="navbar navbar-inverse navbar-fixed-top">
      <div class="navbar-inner">
        <div class="container-fluid">

          <a class="brand" href="#">Online Payment</a>
          <div class="nav-collapse collapse">
            <p class="navbar-text pull-right">
              Logged in as <a href="#" class="navbar-link">Username</a>
            </p>
            <ul class="nav">
              <li><a href="#">账户设置</a></li>
              <li><a href="order_manage.html">我是买家</a></li>
              <li><a href="#contact">我是卖家</a></li>
			  <li class="active"><a href="#contact">淘宝贝</a></li>
			  <li><a href="#contact">在线预订</a></li>
            </ul>
          </div><!--/.nav-collapse -->
        </div>
      </div>
    </div>
   <div class="hero-unit"></div>
   <div class="container-fluid">
	<div class="row-fluid">
		  <div class="span2">
          <div class="well sidebar-nav">
            <ul class="nav nav-list">
              <li class="nav-header">酒店</li>
              <li><a href="hotelbooking.html">酒店预定</a></li>
              <li><a href="innbooking.html">旅馆预定</a></li>			
              <li class="nav-header">航班</li>
              <li><a href="interflight.html">国际航班</a></li>
			  <li class="active"><a href="domeflight.html">国内航班</a></li>
            </ul>
          </div><!--/.well -->
        </div><!--/span-->
        <div class="span10">
  <div class="main">
	  <div class="rimidebox">
		<a href="bookindex.html">预定系统</a><span>>></span><a href="bookindex.html"></a><span><a href="domeflight.html"> 机票预定</a></span>>><span><a href="domeflight.html"> 国内机票搜索</a></span>
      </div>
	  <div class="well sidebar-nav">
	  <div class="order_list">
		<div class="hotelbook">
				<div>
					<label>&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp</label><label><input type="checkbox" class="singletrip" id="singletrip" checked>&nbsp单程</label><label>&nbsp&nbsp&nbsp&nbsp</label><label><input type="checkbox" class="roundtrip" id="roundtrip">&nbsp往返</label>
				</div>
				<div>
					<label> 城市 </label>
					<label> 从：</label>
					<input type="text" size="20" id="departure_city" value maxlength="30">
					<label> 到：</label>
					<input type="text" size="20" id="arrival_city" value maxlength="30">
				</div>
				<li> </li>
				<div>
					<label> &nbsp&nbsp&nbsp&nbsp日期 :&nbsp </label>
					<input type="text" size="20" id="departure_date" value maxlength="30">
					<label>&nbsp&nbsp&nbsp </label>
					<input class="search_button" type="button" value="搜索" 
                        onclick="fetch_flight(
                            $('#departure_city').val(),
                            $('#arrival_city').val(),
                            $('#departure_date').val()
                            )">
				</div>
		</div>		
	   </div>
        <div id='flight_list'></div>
	  </div>
    </div>
		</div>
	</div>
   </div>
  
  <footer class="tail">
		<hr>
        <a href="">关于我们</a>
        <a href="">合作伙伴</a>
        <a href="">联系客服</a>
        <a href="../other/connect_us.html">联系我们</a>
        <a href="../other/map.html">网站地图</a>
        <span>© 2013 Black.com 版权所有</span>
   </footer>
  </body>
  
</html>
