import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
import moment from 'moment';
import LikeButton from "./likeButton";
// The parameter of this function is an object with a string called url inside it.
// url is a prop for the Post component.

export default function Post({ url }) {
  /* Display all info for a single post */

  const [imgUrl, setImgUrl] = useState("");
  const [owner, setOwner] = useState("");
  const [time, setTime] = useState("");
  const [postid, setPostid] = useState("");
  const [likeStatus, setLikeStatus] = useState("");
  const [likeCount, setLikeCount] = useState("");

  useEffect(() => {
    // Declare a boolean flag that we can use to cancel the API request.
    let ignoreStaleRequest = false;

    // Call REST API to get the post's information
    fetch(url, { credentials: "same-origin" })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        // If ignoreStaleRequest was set to true, we want to ignore the results of the
        // the request. Otherwise, update the state to trigger a new render.
        if (!ignoreStaleRequest) {
          setImgUrl(data.imgUrl);
          setOwner(data.owner);
          setTime(moment(data.created).fromNow());
          setPostid(data.postid);
          setLikeStatus(data.likes.lognameLikesThis);
          setLikeCount(data.likes.numLikes);
        }
      })
      .catch((error) => console.log(error));

    return () => {
      // This is a cleanup function that runs whenever the Post component
      // unmounts or re-renders. If a Post is about to unmount or re-render, we
      // should avoid updating state.
      ignoreStaleRequest = true;
    };
  }, [url]);
  // Construct owner url path using owner object
  const ownerUrl = `/users/${  owner  }/`;

  // Double click on img --> post new like, update state
  const handleImgLike = () => {
    // If user originally liked post, do nothing
    // If not, post new like
    if (!likeStatus){
      fetch(`/api/v1/likes/?postid=${postid}`, { method: 'POST' })
        .then(() => {
          setLikeStatus(true);
          setLikeCount(likeCount + 1);
        }); 
    }      
};
  // Render post components
  return (
    <div className="post">
      <p><a href={ownerUrl}>{owner}</a></p>
      <img src={imgUrl} alt="post_image" onDoubleClick={handleImgLike}/>
      <p>{time}</p>
      <p>{postid}</p>
      <LikeButton likeStatus={likeStatus} setLikeStatus={setLikeStatus} likeCount={likeCount} setLikeCount={setLikeCount} postid={postid}/>
      <p>{likeCount} {likeCount === 1 ? 'Like' : 'Likes'}</p>
    </div>
  );
}

Post.propTypes = {
  url: PropTypes.string.isRequired,
};
