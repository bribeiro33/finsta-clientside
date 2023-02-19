import React, { useState } from "react";
import PropTypes from "prop-types";

export default function Comments({ comments, setComments, postid }) {
  const [input, setInput] = useState("");

  // As user types, input changes and is displayed
  const handleChangeComment = (event) => {
    setInput(event.target.value);
  };

  // on form submit, input posted to db as new comment
  const handleSubmitComment = (e) => {
    e.preventDefault();
    fetch(`/api/v1/comments/?postid=${postid}`, {
      // check api like tests for where got headers info
      headers: { "Content-Type": "application/json" },
      credentials: "same-origin",
      method: "POST",
      body: JSON.stringify({ text: input }),
    })
      .then((response) => response.json())
      .then((data) => {
        // Make comment field empty again
        setComments([...comments, data]);
        setInput("");
      })
      .catch((error) => console.log(error));
  };

  // on click of delete button, comment is removed by commentid
  const handleDeleteComment = (e) => {
    e.preventDefault();
    const commentidToRemove = e.target.dataset.option;
    fetch(`/api/v1/comments/${commentidToRemove}/`, {
      credentials: "same-origin",
      method: "DELETE",
    })
      .then(() => {
        console.log(`inside then: ${comments}`);
        setComments(
          comments.filter(
            (comment) => comment.commentid !== parseInt(commentidToRemove, 10)
          )
        );
        console.log(`after setting: ${comments}`);
      })
      .catch((error) => console.log(error));
  };

  return (
    <div>
      {comments.map((comment) => (
        <div key={comment.commentid}>
          <p style={{ display: "inline-block" }}>
            <a href={comment.ownerShowUrl}>
              <strong>{comment.owner}</strong>
            </a>
            &nbsp;&nbsp;
          </p>
          <span className="comment-text" style={{ display: "inline-block" }}>
            {comment.text} &nbsp;&nbsp;
          </span>
          {comment.lognameOwnsThis && (
            <button
              type="button"
              className="delete-comment-button"
              onClick={handleDeleteComment}
              data-option={comment.commentid}
            >
              Delete Comment
            </button>
          )}
        </div>
      ))}
      <form className="comment-form" onSubmit={handleSubmitComment}>
        <span className="comment-text">
          <input
            type="text"
            value={input}
            onChange={handleChangeComment}
            required
          />
        </span>
        <button type="submit" aria-label="Submit" style={{ display: "none" }} />
      </form>
    </div>
  );
}

Comments.propTypes = {
  comments: PropTypes.arrayOf(PropTypes.shape).isRequired,
  setComments: PropTypes.func.isRequired,
  postid: PropTypes.number.isRequired,
};
