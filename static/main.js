function toggleVisible(){
    let current_vis = document.getElementById("collapsible").style.visibility ;
    if(current_vis == "hidden"){
        document.getElementById("collapsible").style.visibility = "visible"
    }
    else {
        document.getElementById("collapsible").style.visibility = "hidden"
    }
}