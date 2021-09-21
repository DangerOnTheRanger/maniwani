import React from 'react';
import Post from './Post';
import { connect } from 'react-redux';

function mapStateToProps(state) {
    return {posts: state.posts};
}

function Thread(props) {
    return (
        <React.Fragment>
          {props.posts.map((post, i) => {
              return <Post {...post}/>;
          })}
        </React.Fragment>
    );
}

export default connect(mapStateToProps)(Thread);
