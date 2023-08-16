import React from 'react';
import ProgressBar from 'react-bootstrap/ProgressBar';

const TrackingProgressBar = ({ status }) => {
  const getProgressBarValue = () => {
    switch (status) {
      case 'queued':
        return 10;
      case 'processing':
        return 60;
      case 'finished':
        return 100;
      default:
        return 0;
    }
  };

  return <ProgressBar now={getProgressBarValue()} label={`${getProgressBarValue()}%`} />;
};

export default TrackingProgressBar;
