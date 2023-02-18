import React, { useState, useEffect } from 'react';
import PropTypes from "prop-types";

export default function LikeButton({ likeStatus, setLikeStatus, likeCount, setLikeCount, postid }) {
    // const { likeStatus, setLikeStatus, likeCount, setLikeCount, postid } = props;

    const handleLikeButton = () => {
        // Use urls from REST API section to Post and Delete
        // If user originally liked post, get likeid and delete like
        if (likeStatus){
            fetch(`/api/v1/posts/${postid}/`, { method: 'GET' })
                .then((response) => {
                    if (!response.ok) throw Error(response.statusText);
                    return response.json();
                })
                .then((data) => {
                    const likeUrl = data.likes.url;
                    // splits URL and removes empty substrings
                    const slashes = likeUrl.split('/').filter(s => s !== '');
                    // gets last substring, should be likeid
                    const likeid = slashes.pop();
                    return fetch(`/api/v1/likes/${likeid}/`, { method: 'DELETE' });
                })
                .then(() => {
                    setLikeStatus(false);
                    setLikeCount(likeCount - 1);
                });
                // .catch((error) => {console.log(error)});
        }
        // If user originally disliked post, POST new like
        else {
            fetch(`/api/v1/likes/?postid=${postid}`, { method: 'POST' })
                .then(() => {
                    setLikeStatus(true);
                    setLikeCount(likeCount + 1);
                }); 
        }      
    };

    return (
        <button type="button" className="like-unlike-button" onClick={handleLikeButton}>
            {likeStatus ? 'Unlike' : 'Like'}
        </button>
    )
}

LikeButton.propTypes = {
    likeStatus: PropTypes.bool.isRequired, 
    setLikeStatus: PropTypes.func.isRequired,
    likeCount: PropTypes.number.isRequired,
    setLikeCount: PropTypes.func.isRequired,
    postid: PropTypes.number.isRequired, // number
};