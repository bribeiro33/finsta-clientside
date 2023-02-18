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
  const [like, setLike] = useState(false);

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
  
  // Render post image and post owner
  return (
    <div className="post">
      <p><a href={ownerUrl}>{owner}</a></p>
      <img src={imgUrl} alt="post_image" />
      <p>{time}</p>
      <p>{postid}</p>
      <LikeButton like={like} setLike={setLike} />
    </div>
  );
}

Post.propTypes = {
  url: PropTypes.string.isRequired,
};
