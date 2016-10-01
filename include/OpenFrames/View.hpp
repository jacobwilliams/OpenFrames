/***********************************
   Copyright 2016 Ravishankar Mathur

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
***********************************/

#ifndef _OF_VIEW_
#define _OF_VIEW_

#include <OpenFrames/Export.h>
#include <OpenFrames/TransformAccumulator.hpp>
#include <osg/Matrixd>
#include <osg/Referenced>
#include <osg/ref_ptr>
#include <osgGA/TrackballManipulator>

namespace OpenFrames
{

/******************************************************************
 * Ravi Mathur
 * OpenFrames API, class View
 * This class encapsulates all the variables needed to describe a view
 * of a scene, namely the modelview and projection matrices.  The modelview
 * matrix is a combination of the viewed ReferenceFrame's transformation
 * matrix and the user's point of view (controlled using the mouse/keyboard).
*****************************************************************/
class OF_EXPORT View : public osg::Referenced
{
  public:
	/** The type of the projection matrix. */
	enum ProjectionType
	{
	  ORTHOGRAPHIC=0, // Object size is independent of distance from viewer
	  PERSPECTIVE, 	// Objects get smaller as they get farther away
	};

        /** The base frame when viewing a ReferenceFrame.
            The camera is assumed to be fixed in this frame when computing
            its user-controlled transformations. */
        enum ViewFrameType
        {
          // View frame initialized to the scene's global reference frame.
          // This is equivalent to an "inertial-fixed" view that follows
          // the body as it translates.
          // If viewing in from-to mode, then the rotation starts in the
          // scene's global reference frame.
          ABSOLUTE=0,

          // View frame initialized to the frame being viewed. This is
          // equivalent to a "body-fixed" view.
          // If viewing in from-to mode, then the rotation starts in the
          // body-fixed reference frame.
          RELATIVE
        };

        /** The method used to rotate the view to look at the "to" frame.
            Since the camera by default looks down the Y-axis, this
            specifies how the Y-axis is rotated to match the vector that
            points to the "to" frame. */
        enum ViewRotationType
        {
          // Single direct rotation, using shortest angle
          // This may result in upside-down view if the rotation angle
          // is greater than 90 degrees out-of-plane
          DIRECT=0,

          // First rotate along X-Y (azimuth), then up Z (elevation)
          // This preserves "Z-up" for the view base frame
          AZEL
        };

	View();
        View(ReferenceFrame *root, ReferenceFrame *viewFrame, ViewFrameType baseframe = RELATIVE);
	View(ReferenceFrame *root, ReferenceFrame *viewFrame, ReferenceFrame *lookatFrame, ViewFrameType frameType = RELATIVE, ViewRotationType rotationType = AZEL);

	/** Get the projection type */
	inline ProjectionType getProjectionType() { return _projType; }

	/** Set a symmetric perspective view. */
	inline void setPerspective(const double fov, const double ratio)
	{
	  _projType = PERSPECTIVE;
	  _projection.makePerspective(fov, _aspectMultiplier*ratio, 1, 10000);
	}

	/** Get the parameters for a symmetric perspective view.  Only valid
	    if a perspective view has been previously set. */
	inline void getPerspective(double &fov, double &ratio) const
	{
	  if(_projType == PERSPECTIVE)
	  {
	    double zNear, zFar;
	    _projection.getPerspective(fov, ratio, zNear, zFar);
	  }
	}

	/** Set/get the constant multiplier that the given aspect ratio (for
	    PERSPECTIVE projections) is multiplied by. This is 1 by default, but
	    can be changed to stretch/squeeze the projection. */
	inline void setAspectMultiplier(double mult)
	{
	  _aspectMultiplier = mult;
	}

	inline double getAspectMultiplier() const { return _aspectMultiplier; }

	/** Set an orthographic projection with the given bounds. */
	inline void setOrthographic(const double left, const double right,
				const double bottom, const double top)
	{
	  _projType = ORTHOGRAPHIC;
	  _projection.makeOrtho(left, right, bottom, top, 1, 10000);
	}

	/** Get the parameters for an orthographic projection.  Only valid if
	    an ortho projection was previously set. */
	inline void getOrthographic(double &left, double &right, 
				double &bottom, double &top) const
	{
	  if(_projType == ORTHOGRAPHIC)
	  {
	    double zNear, zFar;
	    _projection.getOrtho(left, right, bottom, top, zNear, zFar);
	  }
	}

	/** Get the projection and view matrices. */
	inline osg::Matrixd getProjectionMatrix() { return _projection; }
	osg::Matrixd getViewMatrix() { return _trackball->getInverseMatrix(); }

	/** Set the Trackball's default view distance. This is applied when the trackball
	    is reset. A default distance <= 0.0 means that the default distance should
		be auto-computed. */
	void setDefaultViewDistance(double distance) { _defaultViewDistance = distance; }
	double getDefaultViewDistance() const { return _defaultViewDistance; }

	/** Reset the Trackball's home position to the default. */
	void resetTrackball();
	osgGA::TrackballManipulator* getTrackball() const { return _trackball.get(); }

	/** Save the current trackball view as the home view */
	void saveTrackball();

	/** Set the frame to be viewed and the root frame that it should be
	    viewed with respect to. Generally the root frame should be 
            the root of the ReferenceFrame heirarchy that the viewed frame 
            is part of. 
            Optionally, set the reference frame used when viewing the 
            target frame. */
        void setViewFrame( ReferenceFrame* root, ReferenceFrame* viewFrame, ViewFrameType frameType = RELATIVE );

        /** View the lookat frame from the point of view of the base frame.
            Optionally, set the reference frame used when viewing the 
            target frame and the rotation type that should be used to
            rotate from the target to the lookat frame. */
	void setViewBetweenFrames( ReferenceFrame* root, ReferenceFrame* viewFrame, ReferenceFrame* lookatFrame, ViewFrameType frameType = RELATIVE, ViewRotationType rotationType = AZEL );

	/** Get the root/origin frames associated with this View */
	ReferenceFrame* getViewRoot() { return _xform->getRoot(); }
	ReferenceFrame* getViewFrame() { return _xform->getOrigin(); }
        ReferenceFrame* getLookAtFrame() { return _xform_lookat->getOrigin(); }
        ViewFrameType getViewFrameType() { return _frameType; }
        ViewRotationType getViewRotationType() { return _rotationType; }

	inline bool isValid() {return _xform->isValid();}

  protected:
	virtual ~View();
	void _init();

	/** The transform for the origin ReferenceFrame. */
	osg::ref_ptr<TransformAccumulator> _xform;
        ViewFrameType _frameType;

	/** The transform for the look-at ReferenceFrame. */
	osg::ref_ptr<TransformAccumulator> _xform_lookat;
        ViewRotationType _rotationType;

	/** The projection type for this view. */
	ProjectionType _projType;
	double _aspectMultiplier; // For PERSPECTIVE projections

	/** The projection matrix. */
	osg::Matrixd _projection;

	/** Default distance at which to view the frame. */
	double _defaultViewDistance;

	/** The transform for user interactivity. */
	osg::ref_ptr<osgGA::TrackballManipulator> _trackball;
};

} // !namespace OpenFrames

#endif
