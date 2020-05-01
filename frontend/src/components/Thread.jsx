import React from 'react';
import Post from './Post';

export default function Thread(props) {
    return (
        <div className="container" id="thread-container">
          {props.posts.map((post, i) => {
              return <Post {...post}/>;
          })}
        </div>
    );
}
