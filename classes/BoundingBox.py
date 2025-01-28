class BoundingBox:
    _id_ = 0
    BoundingBoxes = {}
    def __init__(self, x1=float, y1=float, x2=float, y2=float, classId=0, trackId=0):
        self.id = BoundingBox._id_
        BoundingBox._id_+=1
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.classId = classId
        self.trackId = trackId
        BoundingBox.BoundingBoxes[id] = self

    def __repr__(self):
        return f"BoundingBox(id={self.id}, x1={self.x1}, y1={self.y1}, x2={self.x2}, y2={self.y2}, classId={self.classId}, trackId={self.trackId})\n"

    @classmethod
    def add(cls, x1, y1, x2, y2, classId=0, trackId=None):
        """Yeni bir BoundingBox oluşturur ve BoundingBoxes'a ekler."""
        new_box = cls(x1, y1, x2, y2, classId, trackId)
        cls.BoundingBoxes[new_box.id] = new_box
        return new_box

    @classmethod
    def edit(cls, box_id, x1=None, y1=None, x2=None, y2=None, classId=None, trackId=None):
        """Belirtilen id'deki BoundingBox nesnesini günceller."""
        if box_id not in cls.BoundingBoxes:
            raise ValueError(f"BoundingBox with id {box_id} does not exist.")

        box = cls.BoundingBoxes[box_id]
        # Parametreleri kontrol edip yalnızca verilen değerleri güncelle
        if x1 is not None:
            box.x1 = x1
        if y1 is not None:
            box.y1 = y1
        if x2 is not None:
            box.x2 = x2
        if y2 is not None:
            box.y2 = y2
        if classId is not None:
            box.classId = classId
        if trackId is not None:
            box.trackId = trackId

        return box