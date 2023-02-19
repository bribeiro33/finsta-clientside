import React from 'react';
import PropTypes from "prop-types";

export default function LikeButton({ likeStatus, setLikeStatus, likeCount, setLikeCount, postid }) {
    const handleLikeButton = () => {
        // Use urls from REST API section to Post and Delete
        // If user originally liked post, get likeid and delete like
        if (likeStatus){
            fetch(`/api/v1/posts/${postid}/`, { credentials: "same-origin", method: 'GET' })
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
                    return fetch(`/api/v1/likes/${likeid}/`, { credentials: "same-origin", method: 'DELETE' });
                })
                .then(() => {
                    // flips like status to false
                    setLikeStatus(false);
                    // decreases like count by one as deleted one like
                    setLikeCount(likeCount - 1);
                })
                .catch((error) => {console.log(error)});
        }
        // If user originally disliked post, POST new like
        else {
            fetch(`/api/v1/likes/?postid=${postid}`, { credentials: "same-origin", method: 'POST' })
            .then((response) => {
                if (!response.ok) throw Error(response.statusText);
                return response.json();
            })
            .then(() => {
                // flips like status to false
                setLikeStatus(true);
                // increases like count by one as added one like
                setLikeCount(likeCount + 1);
            })
            .catch((error) => console.log(error));
        }      
    };

    return (
        <button type="button" className="like-unlike-button" onClick={handleLikeButton}>
            {likeStatus ? 'unlike' : 'like'}
        </button>
    );
}

LikeButton.propTypes = {
    likeStatus: PropTypes.bool.isRequired, 
    setLikeStatus: PropTypes.func.isRequired,
    likeCount: PropTypes.number.isRequired,
    setLikeCount: PropTypes.func.isRequired,
    postid: PropTypes.number.isRequired, 
};