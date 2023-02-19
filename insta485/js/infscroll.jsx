import React, { useState, useEffect } from "react";
import InfiniteScroll from "react-infinite-scroll-component";
import Post from "./post";

export default function InfScroll() {
    const [posts, setPosts] = useState([]);
    const [nextURL, setNextURL] = useState("/api/v1/posts/");

    function fetchData(){
        /*if (this.state.items.length >= 500) {
            this.setState({ hasMore: false });
            return;
        }*/
        // a fake async api call like which sends
        // 20 more records in .5 secs
        fetch(nextURL, {credentials: "same-origin"})
            .then((response) => {
                if (!response.ok) throw Error(response.statusText);
                return response.json();
            })
            .then((data) => {
                // posts stores the posts that are going to be currently 
                setPosts(posts.concat(data['results']));
                setNextURL(data['next']);
            })
            .catch((error) => console.log(error));
    };
    // useEffect calls fetchData to update the posts displayed only when at the bottom of scrolling
    useEffect(() => {
        fetchData();
    }, []);
    return (
        <InfiniteScroll
            dataLength={posts.length} //This is important field to render the next data
            next={fetchData}
            hasMore={nextURL === "" ? false : true}
            loader={<h4>Loading...</h4>}>
            {posts.map((post) => <Post key={post.postid} url={post.url} />)}
        </InfiniteScroll>
    );
}