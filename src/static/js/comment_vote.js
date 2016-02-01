// VOTING logic
// Submit post on submit

function send_vote(json) {
  $.ajax({
      url : "/ajax/comment-vote/",
      type : "POST",
      data : json,
      success : function(json) {
          console.log(json);
          var thumb_up_id = "thumb-up-".concat(json.comment_id);
          var thumb_down_id = "thumb-down-".concat(json.comment_id);
          var total_votes_id = "total-votes-".concat(json.comment_id);
          var comment_credit_id = "comment-credit-".concat(json.comment_id);
          if (json.value == 0) {
            console.log('voting result: 0');
            document.getElementById(thumb_up_id).className = "fa fa-thumbs-o-up";
            document.getElementById(thumb_down_id).className = "fa fa-thumbs-o-down";
            document.getElementById(total_votes_id).innerHTML = json.total;
            document.getElementById(comment_credit_id).innerHTML = parseFloat(json.total_comment_credit).toFixed(1);
          }
          else if (json.value == 1) {
            console.log('voting result: 1');
            document.getElementById(thumb_up_id).className = "fa fa-thumbs-up";
            document.getElementById(thumb_down_id).className = "fa fa-thumbs-o-down";
            document.getElementById(total_votes_id).innerHTML = json.total;
            document.getElementById(comment_credit_id).innerHTML = parseFloat(json.total_comment_credit).toFixed(1);
          }
          else if (json.value == -1) {
            console.log('voting result: -1');
            document.getElementById(thumb_up_id).className = "fa fa-thumbs-o-up";
            document.getElementById(thumb_down_id).className = "fa fa-thumbs-down";
            document.getElementById(total_votes_id).innerHTML = json.total;
            document.getElementById(comment_credit_id).innerHTML = parseFloat(json.total_comment_credit).toFixed(1);
          }
          else {
            console.log('sanity check: voting result: UNKNOWN');
          }
          console.log("success");
      },
      error : function(xhr,errmsg,err) {
          console.log(xhr.status + ": " + xhr.responseText);
      }
  });
}
