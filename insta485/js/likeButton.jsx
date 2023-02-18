import React, { useState } from 'react';

export default function LikeButton(props) {
    const { like, setLike } = props;

    const handleLike = () => {
        setLike(!like);
    };

    return (
        <button type="button" className="like-unlike-button" onClick={handleLike}>
            {like ? 'Unlike' : 'Like'}
        </button>
    )
}