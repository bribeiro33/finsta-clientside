import React from "react";
import PropTypes from "prop-types";

export default function LikeButton({
  likeStatus,
  setLikeStatus,
  likeCount,
  setLikeCount,
  likeUrl,
  setLikeUrl,
  postid,
}) {
  const handleLikeButton = () => {
    // Use urls from REST API section to Post and Delete
    // If user originally liked post, get likeid and delete like
    if (likeStatus) {
      // splits URL and removes empty substrings
      const slashes = likeUrl.split("/").filter((s) => s !== "");
      // gets last substring, should be likeid
      const likeid = slashes.pop();
      // Delete like from api, need credentials
      fetch(`/api/v1/likes/${likeid}/`, {
        credentials: "same-origin",
        method: "DELETE",
        headers: { "Content-Type": "application/json" },
      })
        .then(() => {
          // flips like status to false
          setLikeStatus(false);
          // decreases like count by one as deleted one like
          setLikeCount(likeCount - 1);
        })
        .catch((error) => {
          console.log(error);
        });
    }
    // If user originally disliked post, POST new like
    else {
      fetch(`/api/v1/likes/?postid=${postid}`, {
        credentials: "same-origin",
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
      })
        .then((response) => {
          if (!response.ok) throw Error(response.statusText);
          return response.json();
        })
        .then((data) => {
          // flips like status to false
          setLikeStatus(true);
          // increases like count by one as added one like
          setLikeCount(likeCount + 1);
          // set like url to
          setLikeUrl(data.url);
        })
        .catch((error) => console.log(error));
    }
  };

  return (
    <button
      type="button"
      className="like-unlike-button"
      onClick={handleLikeButton}
    >
      {likeStatus ? "unlike" : "like"}
    </button>
  );
}

LikeButton.propTypes = {
  likeStatus: PropTypes.bool.isRequired,
  setLikeStatus: PropTypes.func.isRequired,
  likeCount: PropTypes.number.isRequired,
  setLikeCount: PropTypes.func.isRequired,
  likeUrl: PropTypes.string.isRequired,
  setLikeUrl: PropTypes.func.isRequired,
  postid: PropTypes.number.isRequired,
};
