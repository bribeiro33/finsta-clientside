import React, { useState, useEffect, useCallback } from "react";
import InfiniteScroll from "react-infinite-scroll-component";
import Post from "./post";

export default function InfScroll() {
  const [posts, setPosts] = useState([]);
  const [nextURL, setNextURL] = useState("/api/v1/posts/");

  const fetchData = useCallback(() => {
    fetch(nextURL, { credentials: "same-origin" })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        // posts stores the posts that are going to be currently
        setPosts(posts.concat(data.results));
        setNextURL(data.next);
      })
      .catch((error) => console.log(error));
  }, [nextURL, posts]);
  // useEffect calls fetchData to update the posts displayed only when at the bottom of scrolling
  useEffect(() => {
    fetchData();
  }, [fetchData]);
  return (
    <InfiniteScroll
      // This is important field to render the next data
      dataLength={posts.length}
      next={fetchData}
      hasMore={nextURL !== ""}
      loader={<h4>Loading...</h4>}
    >
      {posts.map((post) => (
        <Post key={post.postid} url={post.url} />
      ))}
    </InfiniteScroll>
  );
}
