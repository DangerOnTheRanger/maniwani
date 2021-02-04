import React from 'react';
import Post from './Post';
import { connect } from 'react-redux';

function mapStateToProps(state) {
    return {posts: state.posts};
}

function Thread(props) {
    return (
        <div className="container">
          {props.posts.map((post, i) => {
              return <Post {...post}/>;
          })}
        </div>
    );
}

export default connect(mapStateToProps)(Thread);
