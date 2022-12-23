function btnCommentsClick(postId) {
  var button = document.getElementById(postId + "Btn");
  if (button.classList.contains("showButton")) {
    document.getElementById(postId + "CommentTable").style.display = "block";
    document.getElementById(postId + "Btn").classList.remove("showButton");
    document.getElementById(postId + "Btn").classList.add("hideButton");
    document.getElementById(postId + "Btn").textContent = ">Hide Comments"
  } else {
    document.getElementById(postId + "CommentTable").style.display = "none";
    document.getElementById(postId + "Btn").classList.remove("hideButton");
    document.getElementById(postId + "Btn").classList.add("showButton");
    document.getElementById(postId + "Btn").textContent = ">Show Comments"
  }
}