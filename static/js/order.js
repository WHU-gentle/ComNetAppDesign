 var timeId;
 $(document).ready(function(){
 $("li").each(function(index){
 //index是li数组的的索引值
 $(this).mouseover(function(){
 var liNode = $(this);
 var id = $(this).attr('id');
 //延迟是为了减少服务器压力，防止鼠标快速滑动
 timeId = setTimeout(function(){
  //将原来显示的div隐藏掉
  $("div.show").removeClass("show").addClass("hide");
  //将原来的li的active去掉
  $("li.active").removeClass("active");
  //???有问题
  //if(String(Number(id)+6)===$("div").attr('id')){
  // var x=document.getElementsById(String(Number(id)+6));
   //x.removeClass("hide").addClass("show");
  //}
  $("div.hide").eq(index).removeClass("hide").addClass("show");
  liNode.addClass("active");
 },300);
 }).mouseout(function(){
 clearTimeout(timeId);
 });
 });
 });