$.fn.toolBar =  function changeBar(firstAction,secondAction,thirdAction,fourthAction,fifthAction){
    $("#first").click(function(){
        changeBtnState(0);
        if(firstAction){
            firstAction();
        }
    });
    $("#second").click(function(){
        changeBtnState(1);
        if(secondAction){
            secondAction();
        }
    });
    $("#third").click(function(){
        changeBtnState(2);
        if(thirdAction){
            thirdAction();
        }
    });
    $("#fourth").click(function(){
        changeBtnState(3);
        if(fourthAction){
            fourthAction();
        }
    });
    $("#fifth").click(function(){
        changeBtnState(4);
        if(fifthAction){
            fifthAction();
        }
    });
}

function changeBtnState(ind){
    $(".g-nav-list li").each(function(index){
        if(index==ind){
            $(this).attr("class","selected");
        }else{
            $(this).attr("class","none");
        }
    });
}
