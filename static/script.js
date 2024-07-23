"use strict";

let $likeIcon = $(".fa-star");
const BASE_URL = "http://localhost:5000";

async function addLike(msgId) {
  console.debug("addLike");
  try {
    const resp = await axios({
      url: BASE_URL + `/like/${msgId}`,
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    });
    console.debug("resp", resp);
    return resp.data.result;
  } catch (error) {
    console.log("error", error);
  }
  // const resp = await axios({
  //   url: BASE_URL + `/like/${msgId}`,
  //   method: "POST",
  // });

  // return resp.data.result;
}

async function dislike(msgId) {
  console.debug("dislike");
  const resp = await axios({
    url: BASE_URL + `/like/stop-liking/${msgId}`,
    method: "POST",
  });

  return resp.data.result;
  //const resp await delete view
}

async function togglelikeUI(evt) {
  console.debug("toggleLikeUI");
  // let msgStar = evt.target   msg star = solidstar
  //msg =  solid star
  //     dislike
  // msg = emptystar
  //     dislike

  let msgId = evt.target.id;
  let starClass = $(evt.target).attr("class");
  console.log(starClass);
  console.log(msgId);
  let resp;
  if (starClass === "fa-star fas") {
    resp = await dislike(msgId);
  } else if (starClass === "fa-star far") {
    resp = await addLike(msgId);
  }

  if (resp === "like") {
    $(evt.target).removeClass("far");
    $(evt.target).addClass("fas");
  } else if (resp === "dislike") {
    $(evt.target).removeClass("fas");
    $(evt.target).addClass("far");
  }
}

$(".fa-star").on("click", togglelikeUI);
