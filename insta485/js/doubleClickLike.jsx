import React, { useState, useEffect } from 'react';
import PropTypes from "prop-types";

export default function doubleClickLike({ likeStatus, setLikeStatus, likeCount, setLikeCount, postid }) {
    const handleDoubleClickLike = () => {
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

    return (
        <div>
            <button type="button" className="like-unlike-button" onClick={handleDoubleClickLike}>
                {likeStatus ? 'Unlike' : 'Like'}
            </button>
            <p>{likeCount} {likeCount === 1 ? 'Like' : 'Likes'}</p>
        </div>
    )
}


doubleClickLike.propTypes = {
    likeStatus: PropTypes.bool.isRequired, 
    setLikeStatus: PropTypes.func.isRequired,
    likeCount: PropTypes.number.isRequired,
    setLikeCount: PropTypes.func.isRequired,
    postid: PropTypes.number.isRequired,
};