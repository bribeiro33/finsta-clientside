import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
import moment from 'moment';
import LikeButton from "./likeButton";
import Comments from "./comments";
// The parameter of this function is an object with a string called url inside it.
// url is a prop for the Post component.

export default function Post({ url }) {
  /* Display all info for a single post */

  const [imgUrl, setImgUrl] = useState(null);
  const [owner, setOwner] = useState(null);
  const [time, setTime] = useState(null);
  const [postid, setPostid] = useState(null);
  const [likeStatus, setLikeStatus] = useState(null);
  const [likeCount, setLikeCount] = useState(null);
  const [comments, setComments] = useState(null);
  const [postUrl, setPostUrl] = useState(null);
  const [ownerImgUrl, setOwnerImgUrl] = useState(null);
  const [ownerShowUrl, setOwnerShowUrl] = useState(null);

  useEffect( () => {
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
          setTime(moment(moment.utc(data.created).format()).fromNow());
          setPostid(data.postid);
          setLikeStatus(data.likes.lognameLikesThis);
          setLikeCount(data.likes.numLikes);
          setComments(data.comments);
          setPostUrl(data.postShowUrl);
          setOwnerImgUrl(data.ownerImgUrl);
          setOwnerShowUrl(data.ownerShowUrl);
        }
      })
      .then(() => {
        
      })
      .catch((error) => console.log(error));

    return () => {
      // This is a cleanup function that runs whenever the Post component
      // unmounts or re-renders. If a Post is about to unmount or re-render, we
      // should avoid updating state.
      ignoreStaleRequest = true;
    };
  }, [url]);
  // Double click on img --> post new like, update state
  const handleImgLike = () => {
    // If user originally liked post, do nothing
    // If not, post new like
    if (!likeStatus){
      fetch(`/api/v1/likes/?postid=${postid}`, { credentials: "same-origin", method: 'POST' })
        .then((response) => {
          if (!response.ok) throw Error(response.statusText);
          return response.json();
        })
        .then(() => {
          setLikeStatus(true);
          setLikeCount(likeCount + 1);
        })
        .catch((error) => console.log(error));
    }      
  };
  
  // Render post components if state has updated, return empty if not
  if (!comments){
    return <div />
  }

  return (
    <div className="post">
      <img src={ownerImgUrl} alt="post_owner_icon" />
      <p><a href={ownerShowUrl}>{owner}</a></p>
      <img src={imgUrl} alt="post_image" onDoubleClick={handleImgLike}/>
      <p><a href={postUrl}>{time}</a></p>
      <LikeButton likeStatus={likeStatus} setLikeStatus={setLikeStatus} likeCount={likeCount} setLikeCount={setLikeCount} postid={postid}/>
      <p>{likeCount} {likeCount === 1 ? 'like' : 'likes'}</p>
      <Comments comments={comments} setComments={setComments} postid={postid} />
    </div>
  );
}

Post.propTypes = {
  url: PropTypes.string.isRequired,
};
