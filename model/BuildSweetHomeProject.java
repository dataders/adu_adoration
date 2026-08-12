import com.eteks.sweethome3d.io.DefaultHomeOutputStream;
import com.eteks.sweethome3d.model.CatalogPieceOfFurniture;
import com.eteks.sweethome3d.model.Home;
import com.eteks.sweethome3d.model.HomePieceOfFurniture;
import com.eteks.sweethome3d.model.Level;
import com.eteks.sweethome3d.model.Room;
import com.eteks.sweethome3d.model.Wall;
import com.eteks.sweethome3d.tools.URLContent;

import java.io.File;
import java.io.FileOutputStream;


/** Build a Sweet Home 3D project containing the imported Option E model. */
public final class BuildSweetHomeProject {
  private BuildSweetHomeProject() {
  }

  public static void main(String[] args) throws Exception {
    if (args.length != 1) {
      throw new IllegalArgumentException("usage: BuildSweetHomeProject MODEL_DIRECTORY");
    }

    File modelDirectory = new File(args[0]).getCanonicalFile();
    File objFile = new File(modelDirectory, "adu-option-e-sweethome-simple.obj");
    File iconFile = new File(modelDirectory, "adu-option-e-axon.png");
    URLContent model = new URLContent(objFile.toURI().toURL());
    URLContent icon = new URLContent(iconFile.toURI().toURL());
    CatalogPieceOfFurniture catalogPiece = new CatalogPieceOfFurniture(
        "ADU Option E",
        icon,
        model,
        838.2f,
        731.52f,
        609.6f,
        false,
        false);

    writeFloorPlan(
        new File(modelDirectory, "adu-option-e-level-1.sh3d"), catalogPiece, 1);
    writeFloorPlan(
        new File(modelDirectory, "adu-option-e-level-2.sh3d"), catalogPiece, 2);

    // Retain the previously shared filename, but make it an unambiguous clean
    // Level 2 view rather than overlaying the lower floor underneath it.
    writeFloorPlan(
        new File(modelDirectory, "adu-option-e-floorplans.sh3d"), catalogPiece, 2);
  }

  private static void writeFloorPlan(
      File outputFile, CatalogPieceOfFurniture catalogPiece, int floor) throws Exception {
    Home home = new Home();
    home.setName(outputFile.getAbsolutePath());

    Level level;
    if (floor == 1) {
      level = new Level("Level 1 - garage, bath, office, sunroom", 0f, 20.32f, 269.24f);
      home.addLevel(level);
      addLevel1Plan(home, level);
    } else {
      level = new Level("Level 2 - apartment", 289.56f, 20.32f, 299.72f);
      home.addLevel(level);
      addLevel2Plan(home, level);
    }
    home.setSelectedLevel(level);

    // Keep the full imported massing available as a hidden 3D reference.
    HomePieceOfFurniture piece = new HomePieceOfFurniture(catalogPiece);
    piece.setCreator("adu_adoration / FreeCAD");
    piece.setMovable(false);
    piece.setX(piece.getWidth() / 2f);
    piece.setY(piece.getDepth() / 2f);
    piece.setLevel(level);
    piece.setVisible(false);
    home.addPieceOfFurniture(piece);
    home.setSelectedItems(java.util.Collections.emptyList());

    try (DefaultHomeOutputStream output =
             new DefaultHomeOutputStream(new FileOutputStream(outputFile))) {
      output.writeHome(home);
    }

    System.out.printf("wrote %s (%d bytes; floor %d)%n", outputFile, outputFile.length(), floor);
  }

  private static float cm(float feet) {
    return feet * 30.48f;
  }

  private static void addWall(
      Home home, Level level, float x1, float y1, float x2, float y2, float thicknessFeet) {
    Wall wall = new Wall(cm(x1), cm(y1), cm(x2), cm(y2), cm(thicknessFeet), level.getHeight());
    wall.setLevel(level);
    wall.setLeftSideColor(0xE7E3DA);
    wall.setRightSideColor(0xE7E3DA);
    wall.setTopColor(0xA9A69F);
    home.addWall(wall);
  }

  private static void addRoom(
      Home home, Level level, String name, float x, float y, float width, float depth, int color) {
    Room room = new Room(new float[][] {
        {cm(x), cm(y)},
        {cm(x + width), cm(y)},
        {cm(x + width), cm(y + depth)},
        {cm(x), cm(y + depth)}
    });
    room.setName(name);
    room.setLevel(level);
    room.setFloorColor(color);
    room.setCeilingVisible(true);
    home.addRoom(room);
  }

  private static void addShell(Home home, Level level) {
    addWall(home, level, 0.25f, 0.25f, 23.75f, 0.25f, 0.5f);
    addWall(home, level, 23.75f, 0.25f, 23.75f, 19.75f, 0.5f);
    addWall(home, level, 23.75f, 19.75f, 0.25f, 19.75f, 0.5f);
    addWall(home, level, 0.25f, 19.75f, 0.25f, 0.25f, 0.5f);
  }

  private static void addLevel1Plan(Home home, Level level) {
    addShell(home, level);
    addWall(home, level, 14.165f, 0.5f, 14.165f, 19.5f, 0.33f);
    addWall(home, level, 7.5f, 14.165f, 14.0f, 14.165f, 0.33f);
    addWall(home, level, 7.665f, 14.0f, 7.665f, 19.5f, 0.33f);
    addWall(home, level, 14.0f, 14.165f, 23.5f, 14.165f, 0.33f);

    addRoom(home, level, "Garage / storage", 0.5f, 0.5f, 13.5f, 13.5f, 0xD9D9D4);
    addRoom(home, level, "Garage north return", 0.5f, 14.0f, 7.0f, 5.5f, 0xD9D9D4);
    addRoom(home, level, "Bathroom", 7.83f, 14.33f, 5.84f, 5.12f, 0xDDF0E8);
    addRoom(home, level, "Office", 14.33f, 14.33f, 9.12f, 5.12f, 0xF2E8D0);
    addRoom(home, level, "Sunroom", 14.33f, 0.55f, 9.12f, 13.4f, 0xE4D5D0);
  }

  private static void addLevel2Plan(Home home, Level level) {
    addShell(home, level);
    addWall(home, level, 10.365f, 0.5f, 10.365f, 10.0f, 0.33f);
    addWall(home, level, 0.5f, 10.165f, 10.53f, 10.165f, 0.33f);
    addWall(home, level, 7.065f, 10.0f, 7.065f, 16.2f, 0.33f);
    addWall(home, level, 0.5f, 16.365f, 7.23f, 16.365f, 0.33f);
    addWall(home, level, 0.5f, 8.165f, 6.5f, 8.165f, 0.33f);
    addWall(home, level, 12.0f, 7.525f, 18.5f, 7.525f, 0.35f);

    addRoom(home, level, "Bedroom", 0.55f, 0.55f, 9.6f, 9.4f, 0xD5E2F1);
    addRoom(home, level, "Bathroom / laundry", 0.55f, 10.33f, 6.3f, 5.82f, 0xDDF0E8);
    addRoom(home, level, "Linen storage", 0.55f, 16.53f, 6.3f, 2.92f, 0xE2DDF0);
    addRoom(home, level, "Living / dining", 10.55f, 0.55f, 12.9f, 8.1f, 0xF2DCD8);
    addRoom(home, level, "Kitchen / dining", 10.55f, 8.7f, 12.9f, 6.8f, 0xF5E7C9);
  }
}
