import React, { useState, useEffect } from 'react';
import PropTypes from "prop-types";

export default function Comments({ comments, postid }) {
    const [input, setInput] = useState("")
    console.log(comments)
    // As user types, input changes and is displayed
    const handleChangeComment = (event) => {
        setInput(event.target.value);
    }

    // Change to streamline
    const handleSubmitComment = (e) => {
        e.preventDefault();
        fetch(`/api/v1/comments/?postid=${postid}`, {
            headers: {'Content-Type': 'application/json'},
            credentials: 'same-origin',
            method: 'POST',
            body: JSON.stringify({text: input})
        }).then((response) => response.json())
        .then(() => {
            // Make comment field empty again
            setInput("");
        })
        .catch(error => console.log(error));  
    }

    return (
        <div>
            {
                comments.map((comment) => (
                    <div>
                        <p><a href={ comment.ownerShowUrl }>
                            { comment.owner };
                        </a></p>
                        <span className="comment-text"> 
                            { comment.text }
                        </span>
                    </div>
                ))
            }
            <form className="comment-form" onSubmit={ handleSubmitComment }>
                <span className="comment-text">
                    <input type="text" value={ input } onChange={ handleChangeComment } required/>
                </span>     
                <button type="submit" aria-label="Submit" style={{ display: 'none' }} />
            </form>
        </div>
    )
}

Comments.propTypes = {
    comments: PropTypes.arrayOf(PropTypes.number, PropTypes.bool, PropTypes.string, PropTypes.string, PropTypes.string, PropTypes.string).isRequired,
    postid: PropTypes.number.isRequired, // number
};