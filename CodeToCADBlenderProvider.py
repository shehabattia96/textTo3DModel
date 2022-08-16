import math
import CodeToCAD.utilities as Utilities
import BlenderDefinitions
import BlenderActions

from pathlib import Path

def debugOnReceiveBlenderDependencyGraphUpdateEvent(scene, depsgraph):
    for update in depsgraph.updates:
        print("Received Event: {} Type: {}".format(update.id.name, type(update.id)))

BlenderActions.addDependencyGraphUpdateListener(debugOnReceiveBlenderDependencyGraphUpdateEvent)

min = "min"
max = "max"
center = "center"

class Entity:

    def translate_fromstring(self,
        translateString:str
    ):
        dimensions:list[Utilities.Dimension] = Utilities.getDimensionsFromStringList(translateString)

        dimensions = BlenderDefinitions.BlenderLength.convertDimensionsToBlenderUnit(dimensions)

        while len(dimensions) < 3:
            dimensions.append(Utilities.Dimension(1))
    
        BlenderActions.translateObject(self.name, dimensions, BlenderDefinitions.BlenderTranslationTypes.RELATIVE)

        return self

    def translate(self,
        translateX:str,
        translateY:str,
        translateZ:str
    ):
        return self.translate_fromstring([translateX, translateY, translateZ])
        

    def setPosition_fromstring(self,
    dimensions:str\
    ):
        dimensions:list[Utilities.Dimension] = Utilities.getDimensionsFromStringList(dimensions) or []
        
        dimensions = BlenderDefinitions.BlenderLength.convertDimensionsToBlenderUnit(dimensions)

        while len(dimensions) < 3:
            dimensions.append(Utilities.Dimension(1))

        BlenderActions.setObjectLocation(self.name, dimensions)

        return self
        
    def setPosition(self,
        postitionX:str,
        positionY:str,
        positionZ: str
    ):
        return self.setPosition_fromstring([postitionX, positionY, positionZ])

    def scale_fromstring(self,
    dimensions:str
    ):
        if type(dimensions) is str:
            dimensions = dimensions.replace(" ","").lower().split(",")

        # special case for scaling aspect ratio
        dimensions = [
            BlenderDefinitions.BlenderLength.convertDimensionToBlenderUnit(
                Utilities.Dimension.fromString(dimension)
            )
            if dimension else None for dimension in dimensions
        ]
    
        BlenderActions.scaleObject(self.name, dimensions)
        
        BlenderActions.applyObjectRotationAndScale(self.name)
        
        return self

    def scale(self,
        scaleX,
        scaleY,
        scaleZ
    ):
        return self.scale_fromstring([scaleX, scaleY, scaleZ])

    def scale_aspect_ratio(self,
        scaleValue:str,
        axisToScale:str
    ):
        axis = Utilities.Axis.fromString(axisToScale).value
        
        ratio = [None, None, None]
        ratio[axis] = scaleValue

        return self.scale_fromstring(ratio)


    def rotate_fromstring(self,
    rotation:str \
    ):
        angleList:list[Utilities.Angle] = Utilities.getAnglesFromStringList(rotation)
    
        BlenderActions.rotateObject(self.name, angleList, BlenderDefinitions.BlenderRotationTypes.EULER)

        BlenderActions.applyObjectRotationAndScale(self.name)

        return self
    
    def rotate(self,
        rotateX:str,
        rotateY:str,
        rotateZ:str
    ):
        return self.rotate_fromstring([rotateX, rotateY, rotateZ])

    def rename(self,
    newName:str,
    renameData = True,
    renameLandmarks = True
    ):
        BlenderActions.updateObjectName(self.name, newName)

        if renameData:
            BlenderActions.updateObjectDataName(newName, newName)

        if renameLandmarks:
            BlenderActions.updateObjectLandmarkNames(newName, self.name, newName)

        return self


    def clone(self,
    newPartName:str,
    copyLandmarks:bool = True
    ):
        BlenderActions.duplicateObject(self.name, newPartName, copyLandmarks)

        return Part(newPartName)
        
    def revolve(self,
    angle:str,
    axis:str,
    entityNameToDetermineAxis = None
    ):
        if isinstance(entityNameToDetermineAxis, Entity): entityNameToDetermineAxis = entityNameToDetermineAxis.name

        axis = Utilities.Axis.fromString(axis)

        assert axis, f"Unknown axis {axis}. Please use 'x', 'y', or 'z'"

        BlenderActions.applyScrewModifier(self.name, Utilities.Angle.fromString(angle).toRadians(), axis, entityNameToDetermineAxis=entityNameToDetermineAxis)

        return self

    def thicken(self,
    thickness:float
    ):
        BlenderActions.applySolidifyModifier(self.name, Utilities.Dimension.fromString(thickness))

        return self
        
    def screw(self,
    angle:str,
    axis:str,
    screwPitch:str = 0,
    iterations:int = 1
    ):
        axis = Utilities.Axis.fromString(axis)

        assert axis, f"Unknown axis {axis}. Please use 'x', 'y', or 'z'"
        
        BlenderActions.applyScrewModifier(self.name, Utilities.Angle.fromString(angle).toRadians(), axis, screwPitch=Utilities.Dimension.fromString(screwPitch), iterations=iterations)
        
        return self

    def remesh(self,
    strategy:str = None,  \
    amount:float = None \
    ):
    
        BlenderActions.applyModifier(self.name, BlenderDefinitions.BlenderModifiers.EDGE_SPLIT, {"name": "EdgeDiv", "split_angle": math.radians(30)})
        
        BlenderActions.applyModifier(self.name, BlenderDefinitions.BlenderModifiers.SUBSURF, {"name": "Subdivision", "levels": 2})

        return self

    def mirror(self,
    mirrorAcrossEntityName:str, \
    axis:str
    ):
    
        if isinstance(mirrorAcrossEntityName, Entity): mirrorAcrossEntityName = mirrorAcrossEntityName.name
    
        axis = Utilities.Axis.fromString(axis)

        assert axis, f"Unknown axis {axis}. Please use 'x', 'y', or 'z'"

        BlenderActions.applyMirrorModifier(self.name, mirrorAcrossEntityName, axis)
        
        return self

    def linearPattern(self,
        instanceCount,
        directionAxis:str,
        offset:str,
    ):

        axis = Utilities.Axis.fromString(directionAxis)
        
        assert axis, f"Unknown axis {axis}. Please use 'x', 'y', or 'z'"

        offset = Utilities.Dimension.fromString(offset)
        offset = BlenderDefinitions.BlenderLength.convertDimensionToBlenderUnit(offset)
        offset = offset.value
        
        BlenderActions.applyLinearPattern(self.name, instanceCount, axis, offset)

        return self

    def circularPattern(self,
        instanceCount,
        separationAngle,
        normalDirectionAxis:str,
        centerPartName,
        centerLandmarkName = None
    ):

        if isinstance(centerPartName, Entity): centerPartName = centerPartName.name
        if isinstance(centerLandmarkName, Landmark): centerLandmarkName = centerLandmarkName.landmarkName

        centerObjectName = Landmark(centerPartName, centerLandmarkName).entityName if centerLandmarkName else centerPartName

        pivotLandmark = Landmark("circularPatternPivot", self.name)

        self.createLandmark(pivotLandmark.landmarkName, 0, 0, 0)
        
        BlenderActions.applyPivotConstraint(pivotLandmark.entityName, centerObjectName)
        
        axis = Utilities.Axis.fromString(normalDirectionAxis)

        assert axis, f"Unknown axis {axis}. Please use 'x', 'y', or 'z'"

        angles = [Utilities.Angle(0) for _ in range(3)]
        angles[axis.value] = Utilities.Angle.fromString(separationAngle)
        
        BlenderActions.rotateObject(pivotLandmark.entityName, angles, BlenderDefinitions.BlenderRotationTypes.EULER)
        
        BlenderActions.applyCircularPattern(self.name, instanceCount, pivotLandmark.entityName)

        return self

    def contourPattern(self
    ):
        print("contourPattern is not implemented") # implement 
        return self


    def delete(self,
        removeChildren = True
    ):
        BlenderActions.removeObject(self.name, removeChildren)
        
        return self
    
    # This is a blender specific action to apply the dependency graph modifiers onto a mesh
    def apply(self):
        
        BlenderActions.applyDependencyGraph(self.name)
        
        BlenderActions.removeMesh(self.name)
        
        BlenderActions.updateObjectDataName(self.name, self.name)

        BlenderActions.clearModifiers(self.name)

        return self
        
    def createLandmarkRelative(
            self,
            landmarkName,
            otherEntityName,
            otherLandmarkName,
            offsetX,
            offsetY,
            offsetZ
        ):
        
        if isinstance(otherEntityName, Entity): otherEntityName = otherEntityName.name
        if isinstance(otherLandmarkName, Landmark): otherLandmarkName = otherLandmarkName.landmarkName

        landmark = Landmark(landmarkName, self.name)
        landmarkObjectName = landmark.entityName
        
        # Create an Empty object to represent the landmark
        # Using an Empty object allows us to parent the object to this Empty.
        # Parenting inherently transforms the landmark whenever the object is translated/rotated/scaled.
        # This might not work in other CodeToCAD implementations, but it does in Blender
        Part(landmarkObjectName).createPrimitive("Empty", "0")
        
        # Assign the landmark to the parent's collection
        BlenderActions.assignObjectToCollection(landmarkObjectName, BlenderActions.getObjectCollection(self.name))

        # Parent the landmark to the object
        BlenderActions.makeParent(landmarkObjectName, self.name)

        BlenderActions.translateLandmarkRelativeToAnother(
            self.name,
            landmarkObjectName,
            otherEntityName,
            otherLandmarkName,
            [Utilities.Dimension.fromString(offset) for offset in [offsetX or 0, offsetY or 0, offsetZ or 0]]
        )

        return landmark

    def createLandmark_fromString(self, landmarkName, localPositionXYZ:str):

        boundingBox = BlenderActions.getBoundingBox(self.name)
        
        localPositions = Utilities.getDimensionsFromStringList(localPositionXYZ, boundingBox)

        assert len(localPositions) == 3, "localPositions should contain 3 dimensions for XYZ"

        localPositions = BlenderDefinitions.BlenderLength.convertDimensionsToBlenderUnit(localPositions)
        
        landmark = Landmark(landmarkName, self.name)
        landmarkObjectName = landmark.entityName
        
        # Create an Empty object to represent the landmark
        # Using an Empty object allows us to parent the object to this Empty.
        # Parenting inherently transforms the landmark whenever the object is translated/rotated/scaled.
        # This might not work in other CodeToCAD implementations, but it does in Blender
        Part(landmarkObjectName).createPrimitive("Empty", "0")

        # Assign the landmark to the parent's collection
        BlenderActions.assignObjectToCollection(landmarkObjectName, BlenderActions.getObjectCollection(self.name))

        # Parent the landmark to the object
        BlenderActions.makeParent(landmarkObjectName, self.name)

        BlenderActions.translateObject(landmarkObjectName, localPositions, BlenderDefinitions.BlenderTranslationTypes.ABSOLUTE)

        return landmark



    def createLandmark(self, landmarkName, localXPosition, localYPosition, localZPosition):
        return self.createLandmark_fromString(landmarkName, [localXPosition, localYPosition, localZPosition])
        

    def setVisible(self,
    isVisible:bool \
    ):
        
        BlenderActions.setObjectVisibility(self.name, isVisible)

        return self

    def getNativeInstance(self
    ): 
        return BlenderActions.getObject(self.name)
        
    def select(self,
    landmarkName:str,  \
    selectionType:str = "face" \
    ):
        landmarkObject = Landmark(landmarkName, self.name)
        landmarkLocation = BlenderActions.getObjectWorldLocation(landmarkObject.entityName)
        [closestPoint, normal, blenderPolygon, blenderVertices] = BlenderActions.getClosestPointsToVertex(self.name, landmarkLocation)

        if blenderVertices != None:
            for vertex in blenderVertices:
                vertex.select = True

        return self

class Part(Entity):

    name = None
    description = None

    def __init__(self,
    name:str, \
    description:str=None \
    ):
        self.name = name
        self.description = description

    def createFromFile(self,
    filePath:str,  \
    fileType:str=None \
    ):
    
        path = Path(filePath)

        fileName = path.stem
        
        BlenderActions.importFile(filePath, fileType)
        
        # Since we're using Blender's bpy.ops API, we cannot provide a name for the newly created object,
        # therefore, we'll use the object's "expected" name and rename it to what it should be
        # note: this will fail if the "expected" name is incorrect
        Part(fileName).rename(self.name)
        
        return self

    def createPrimitive(self,
    primitiveName:str,  \
    dimensions:str,  \
    keywordArguments:dict=None \
    ):
        # TODO: account for blender auto-renaming with sequential numbers
        primitiveType = getattr(BlenderDefinitions.BlenderObjectPrimitiveTypes, primitiveName.lower(), None)
        expectedNameOfObjectInBlender = primitiveType.defaultNameInBlender() if primitiveType else None

        assert expectedNameOfObjectInBlender != None, \
            f"Primitive type with name {primitiveName} is not supported."
        
        BlenderActions.addPrimitive(primitiveType, dimensions, keywordArguments)

        # Since we're using Blender's bpy.ops API, we cannot provide a name for the newly created object,
        # therefore, we'll use the object's "expected" name and rename it to what it should be
        # note: this will fail if the "expected" name is incorrect
        Part(expectedNameOfObjectInBlender).rename(self.name, primitiveType.hasData())

        return self

    def createCube(self,
    width:str,  \
    length:str,  \
    height:str,  \
    keywordArguments:dict=None \
    ):
        return self.createPrimitive("cube", "{},{},{}".format(width,length,height), keywordArguments)

    def createCone(self,
    radius:str,  \
    height:str,  \
    draftRadius:str,  \
    keywordArguments:dict=None \
    ):
        return self.createPrimitive("cone", "{},{},{}".format(radius,height,draftRadius), keywordArguments)

    def createCylinder(self,
    radius:str,  \
    height:str,  \
    keywordArguments:dict=None \
    ):
        return self.createPrimitive("cylinder", "{},{}".format(radius,height), keywordArguments)

    def createGear(
            self,
            outerRadius:str,
            addendum:str,
            innerRadius:str,
            dedendum:str, 
            height:str,
            pressureAngle:str = "20d",
            numberOfTeeth:int = 12,
            skewAngle:str = 0,
            conicalAngle:str = 0,
            crownAngle:str = 0
        ):
            BlenderActions.createGear(
                self.name,
                numberOfTeeth,
                pressureAngle,
                addendum,
                dedendum,
                outerRadius,
                innerRadius,
                height,
                skewAngle,
                conicalAngle,
                crownAngle
            )
            
            # Since we're using Blender's bpy.ops API, we cannot provide a name for the newly created object,
            # therefore, we'll use the object's "expected" name and rename it to what it should be
            # note: this will fail if the "expected" name is incorrect
            Part("Gear").rename(self.name, True)

            return self

    def createTorus(self,
    innerRadius:str,  \
    outerRadius:str,  \
    keywordArguments:dict=None \
    ):
        return self.createPrimitive("torus", "{},{}".format(innerRadius,outerRadius), keywordArguments)

    def createSphere(self,
    radius:str,  \
    keywordArguments:dict=None \
    ):
        return self.createPrimitive("uvsphere", "{}".format(radius), keywordArguments)


    def verticies(self,
    landmarkName:str \
    ):
        print("verticies is not implemented") # implement 
        return self

    def loft(self,
    part1Name:str,  \
    part2Name:str \
    ):
        print("loft is not implemented") # implement 
        return self

    

    def mask(self,
    partName:str,  \
    landmarkName:str \
    ):
        print("mask is not implemented") # implement 
        return self
    

    def union(self,
    withPartName:str \
    ):
        if isinstance(withPartName, Entity): withPartName = withPartName.name

        BlenderActions.applyBooleanModifier(
                        self.name,
                        BlenderDefinitions.BlenderBooleanTypes.UNION,
                        withPartName
                    )

        return self

    def subtract(self,
    withPartName:str \
    ):
        if isinstance(withPartName, Entity): withPartName = withPartName.name

        BlenderActions.applyBooleanModifier(
                    self.name,
                    BlenderDefinitions.BlenderBooleanTypes.DIFFERENCE,
                    withPartName
                )

        return self

    def intersect(self,
    withPartName:str \
    ):
        if isinstance(withPartName, Entity): withPartName = withPartName.name

        BlenderActions.applyBooleanModifier(
                        self.name,
                        BlenderDefinitions.BlenderBooleanTypes.INTERSECT,
                        withPartName
                    )

        return self

    def bevel(self,
    landmarkName:str,  \
    angle:float,  \
    roundedness:int \
    ):
        print("bevel is not implemented") # implement 
        return self

    def hollow(self,
    wallThickness:float \
    ):
        print("hollow is not implemented") # implement 
        return self

# alias for Part
Shape = Part

class Sketch(Entity):
    
    name = None
    curveType = None
    description = None

    def __init__(self,
    name:str, \
    curveType:Utilities.CurveTypes=None, \
    description:str=None \
    ):
        self.name = name
        self.curveType = curveType
        self.description = description


    def extrude(self,
    length:str \
    ):
        
        BlenderActions.extrude(self.name, Utilities.Dimension.fromString(length))

        return self

    def sweep(self,
        profileCurveName,
        fillCap = False
        ):
        
        if isinstance(profileCurveName, Entity): profileCurveName = profileCurveName.name
        
        BlenderActions.addBevelObjectToCurve(self.name, profileCurveName, fillCap)

        return self
        
    def profile(self,
        profileCurveName
        ):
        
        if isinstance(profileCurveName, Entity): profileCurveName = profileCurveName.name

        BlenderActions.applyCurveModifier(self.name, profileCurveName)

        return self

    def createText(self,
        text,
        size = "1m",
        bold = False,
        italic = False,
        underlined = False,
        characterSpacing = 1,
        wordSpacing = 1,
        lineSpacing = 1,
        fontFilePath = None
        ):

        size = Utilities.Dimension.fromString(size)

        BlenderActions.createText(self.name, text, size, bold, italic, underlined, characterSpacing, wordSpacing, lineSpacing, fontFilePath)

        return self

    def createFromVerticies(self,
        coordinates, \
        interpolation = 64 \
        ):

        BlenderActions.createCurve(self.name, BlenderDefinitions.BlenderCurveTypes.fromCurveTypes(self.curveType) if self.curveType != None else BlenderDefinitions.BlenderCurveTypes.BEZIER, coordinates, interpolation)

        return self


    def createPrimitiveDecorator(curvePrimitiveType:Utilities.CurvePrimitiveTypes):
        def decorator(primitiveFunction):
            def wrapper(*args, **kwargs):

                self = args[0]

                blenderCurvePrimitiveType = BlenderDefinitions.BlenderCurvePrimitiveTypes.fromCurvePrimitiveTypes(curvePrimitiveType)

                blenderPrimitiveFunction = BlenderActions.getBlenderCurvePrimitiveFunction(blenderCurvePrimitiveType)

                blenderPrimitiveFunction(
                        *args[1:],
                        dict(
                                {"curveType": BlenderDefinitions.BlenderCurveTypes.fromCurveTypes(self.curveType) if self.curveType != None else None}
                                , **kwargs
                            )
                        )

                
                # Since we're using Blender's bpy.ops API, we cannot provide a name for the newly created object,
                # therefore, we'll use the object's "expected" name and rename it to what it should be
                # note: this will fail if the "expected" name is incorrect
                Part(blenderCurvePrimitiveType.name).rename(self.name)

                return primitiveFunction(*args, **kwargs)
            return wrapper
        return decorator

    @createPrimitiveDecorator(Utilities.CurvePrimitiveTypes.Point)
    def createPoint(self, keywordArguments = {}):
        return self
    @createPrimitiveDecorator(Utilities.CurvePrimitiveTypes.LineTo)
    def createLineTo(self, endLocation, keywordArguments = {}):
        return self
    @createPrimitiveDecorator(Utilities.CurvePrimitiveTypes.Line)
    def createLine(self, length, keywordArguments = {}):
        return self
    @createPrimitiveDecorator(Utilities.CurvePrimitiveTypes.Angle)
    def createAngle(self, length, angle, keywordArguments = {}):
        return self
    @createPrimitiveDecorator(Utilities.CurvePrimitiveTypes.Circle)
    def createCircle(self, radius, keywordArguments = {}):
        return self
    @createPrimitiveDecorator(Utilities.CurvePrimitiveTypes.Ellipse)
    def createEllipse(self, radius_x, radius_y, keywordArguments = {}):
        return self
    @createPrimitiveDecorator(Utilities.CurvePrimitiveTypes.Arc)
    def createArc(self, radius, angle, keywordArguments = {}):
        return self
    @createPrimitiveDecorator(Utilities.CurvePrimitiveTypes.Sector)
    def createSector(self, radius, angle, keywordArguments = {}):
        return self
    @createPrimitiveDecorator(Utilities.CurvePrimitiveTypes.Segment)
    def createSegment(self, outter_radius, inner_radius, angle, keywordArguments = {}):
        return self
    @createPrimitiveDecorator(Utilities.CurvePrimitiveTypes.Rectangle)        
    def createRectangle(self, length, width, keywordArguments = {}):
        return self
    @createPrimitiveDecorator(Utilities.CurvePrimitiveTypes.Rhomb)
    def createRhomb(self, length, width, keywordArguments = {}):
        return self
    @createPrimitiveDecorator(Utilities.CurvePrimitiveTypes.Polygon)
    def createPolygon(self, numberOfSides, radius, keywordArguments = {}):
        return self
    @createPrimitiveDecorator(Utilities.CurvePrimitiveTypes.Polygon_ab)
    def createPolygon_ab(self, numberOfSides, radius_x, radius_y, keywordArguments = {}):
        return self
    @createPrimitiveDecorator(Utilities.CurvePrimitiveTypes.Trapezoid)
    def createTrapezoid(self, length_upper, length_lower, height, keywordArguments = {}):
        return self

# alias for Sketch
Curve = Sketch

class Landmark: 
    # Text to 3D Modeling Automation Capabilities.

    localToEntityWithName = None
    landmarkName = None
    entityName = None

    def __init__(self,
    landmarkName:str,
    localToEntityWithName:str=None \
    ):
    
        if isinstance(localToEntityWithName, Entity): localToEntityWithName = localToEntityWithName.name

        self.localToEntityWithName = localToEntityWithName
        
        self.landmarkName = landmarkName
        
        if localToEntityWithName:
            self.entityName = f"{localToEntityWithName}_{landmarkName}"
        else:
            self.entityName = landmarkName


class Joint: 
    # Text to 3D Modeling Automation Capabilities.

    part1Landmark:Landmark = None
    part2Landmark:Landmark = None

    def __init__(self,
    part1Name:Part, \
    part2Name:Part, \
    part1LandmarkName:Landmark = None, \
    part2LandmarkName:Landmark = None
    ):
        self.part1 = part1Name if isinstance(part1Name, Entity) else Part(part1Name)
        self.part2 = part2Name if isinstance(part2Name, Entity) else Part(part2Name)
        self.part1Landmark = part1LandmarkName if type(part1LandmarkName) is Landmark else \
            Landmark(part1LandmarkName, part1Name) if part1LandmarkName else None
        self.part2Landmark = part2LandmarkName if type(part2LandmarkName) is Landmark else \
            Landmark(part2LandmarkName, part2Name) if part2LandmarkName else None

        
    def translateLandmarkOntoAnother(self):
        
        BlenderActions.translateLandmarkOntoAnother(self.part1.name, self.part2.name, self.part1Landmark.entityName, self.part2Landmark.entityName)

        return self

    @staticmethod
    def _getLocationPair(minLocation:str, maxLocation:str):
        minLocation = Utilities.Dimension.fromString(minLocation) if minLocation != None else None
        maxLocation = Utilities.Dimension.fromString(maxLocation) if maxLocation != None else None

        if minLocation == None and maxLocation == None:
            return None

        if maxLocation and minLocation == None:
            minLocation = Utilities.Dimension(0)

        if minLocation and maxLocation == None:
            maxLocation = Utilities.Dimension(minLocation.value, minLocation.unit)

        return [minLocation, maxLocation]

    @staticmethod
    def _limitLocationOffsetFromLandmark(objectName, objectLandmarkName, relativeToLandmarkName, xDimensions, yDimensions, zDimensions, keywordArguments):

        BlenderActions.updateViewLayer()

        [x,y,z] = BlenderActions.getObjectWorldLocation(objectName) - BlenderActions.getObjectWorldLocation(objectLandmarkName)
        

        if xDimensions:
            for index in range(0,len(xDimensions)):
                xDimensions[index].value = xDimensions[index].value + x
        if yDimensions:
            for index in range(0,len(yDimensions)):
                yDimensions[index].value = yDimensions[index].value + y
        if zDimensions:
            for index in range(0,len(zDimensions)):
                zDimensions[index].value = zDimensions[index].value + z


        BlenderActions.applyLimitLocationConstraint(objectName, xDimensions, yDimensions, zDimensions, relativeToLandmarkName, keywordArguments)

    def limitLocation(
        self,
        minX:str = None,
        minY:str = None,
        minZ:str = None,
        maxX:str = None,
        maxY:str = None,
        maxZ:str = None,
        keywordArguments = {}
        ):
        
        xDimensions = Joint._getLocationPair(minX, maxX)
        yDimensions = Joint._getLocationPair(minY, maxY)
        zDimensions = Joint._getLocationPair(minZ, maxZ)

        
        Joint._limitLocationOffsetFromLandmark(self.part2.name, self.part2Landmark.entityName, self.part1Landmark.entityName, xDimensions, yDimensions, zDimensions, keywordArguments)

        return self
        
    @staticmethod
    def _getAnglePair(minAngle:str, maxAngle:str):
        minAngle = Utilities.Angle.fromString(minAngle) if minAngle != None else None
        maxAngle = Utilities.Angle.fromString(maxAngle) if maxAngle != None else None

        if minAngle == None and maxAngle == None:
            return None

        if maxAngle and minAngle == None:
            minAngle = Utilities.Angle(0)

        if minAngle and maxAngle == None:
            maxAngle = Utilities.Angle(minAngle.value, minAngle.unit)

        return [minAngle, maxAngle]


    def limitRotation(
        self,
        minX:str = None,
        minY:str = None,
        minZ:str = None,
        maxX:str = None,
        maxY:str = None,
        maxZ:str = None,
        keywordArguments = {}
        ):

        xAngles = Joint._getAnglePair(minX, maxX)
        yAngles = Joint._getAnglePair(minY, maxY)
        zAngles = Joint._getAnglePair(minZ, maxZ)
        
        BlenderActions.applyLimitRotationConstraint(self.part2.name, xAngles, yAngles, zAngles, self.part1Landmark.entityName, keywordArguments)

        return self
        
    def pivot(
        self,
        keywordArguments = {}
        ):

        BlenderActions.applyPivotConstraint(self.part2.name, self.part1Landmark.entityName, keywordArguments)

        return self
        
    def gearRatio(
        self,
        ratio:float,
        keywordArguments = {}
        ):

        BlenderActions.applyGearConstraint(self.part2.name, self.part1.name, ratio, keywordArguments)

        return self

class Material: 
    # Text to 3D Modeling Automation Capabilities.


    def __init__(self
    ):
        pass


class Scene: 
    # Text to 3D Modeling Automation Capabilities.

    name = None
    description = None

    # Names a scene
    def __init__(self,
    name:str = "Scene", # Uses Blender's default Scene
    description:str=None \
    ):
        self.name = name
        self.description = description

    def create(self):
        print("create is not implemented") # implement 
        return self

    def delete(self):
        print("delete is not implemented") # implement 
        return self

    def export(self
    ):
        print("export is not implemented") # implement 
        return self

    def setDefaultUnit(self,
    unit:Utilities.LengthUnit \
    ):

        if type(unit) == str:
            unit = Utilities.LengthUnit.fromString(unit)
            
        unit = BlenderDefinitions.BlenderLength.fromLengthUnit(unit)

        BlenderActions.setDefaultUnit(unit, self.name)

        return self

    def createGroup(self,
    name:str \
    ):
        BlenderActions.createCollection(name, self.name)

        return self

    def deleteGroup(self,
    name:str,  \
    removeChildren:bool \
    ):
        BlenderActions.removeCollection(name, removeChildren)

        return self
        
    def removeFromGroup(self,
    entityName:str, \
    groupName:str \
    ):
        if isinstance(entityName, Entity): entityName = entityName.name

        BlenderActions.removeObjectFromCollection(entityName, groupName)

        return self

        
    def assignToGroup(self,
    entityName:str, \
    groupName:str, \
    removeFromOtherGroups:bool = True \
    ):
        if isinstance(entityName, Entity): entityName = entityName.name

        BlenderActions.assignObjectToCollection(entityName, groupName, self.name, removeFromOtherGroups)

        return self
        

    def setVisible(self,
    entityName:str, \
    isVisible:bool \
    ):
        if isinstance(entityName, Entity): entityName = entityName.name

        BlenderActions.setObjectVisibility(entityName, isVisible)

        return self

class Analytics: 
    # Text to 3D Modeling Automation Capabilities.

    def measureLandmarks(self,
    landmark1Name:str,  \
    landmark2Name:str=None \
    ):
        print("measure is not implemented") # implement 
        return None

    def getWorldPose(self,
    partName:str \
    ):
        if isinstance(partName, Entity): partName = partName.name
        return BlenderActions.getObjectWorldPose(partName)

    def getBoundingBox(self,
    partName:str \
    ):
        if isinstance(partName, Entity): partName = partName.name

        return BlenderActions.getBoundingBox(partName)

    def getDimensions(self,
    partName:str \
    ):
        if isinstance(partName, Entity): partName = partName.name
        
        dimensions = BlenderActions.getObject(partName).dimensions
        return [
            Utilities.Dimension.fromString(
                dimension,
                BlenderDefinitions.BlenderLength.DEFAULT_BLENDER_UNIT.value
            ) 
            for dimension in dimensions
            ]
