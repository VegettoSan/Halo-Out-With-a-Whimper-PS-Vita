import java.io.*;
import java.nio.charset.Charset;
import java.nio.file.*;
import java.nio.file.Path;
import java.util.*;
import org.lateralgm.components.impl.ResNode;
import org.lateralgm.file.*;
import org.lateralgm.resources.*;
import org.lateralgm.resources.sub.*;
import org.lateralgm.resources.library.LibManager;

/** Read-only inventory using the local Gmk-Splitter/LateralGM jar, retaining IDs.
 * Outputs may contain proprietary GML: destination MUST be an ignored private directory.
 * Compile with javac -cp <gmksplit.jar> -d <private-class-dir> tools/GmkAudit.java.
 * Use process-local preferences (see tools/MemoryPrefsFactory.java).
 */
public final class GmkAudit {
    public static void main(String[] args) throws Exception {
        Path source = Path.of(args[0]);
        Path output = Path.of(args[1]);
        Files.createDirectory(output); // Refuse overwrite of a previous audit.
        LibManager.autoLoad();
        GmFile game;
        try (InputStream input = Files.newInputStream(source)) {
            game = GmFileReader.readGmFile(input, source.toUri(),
                new ResNode("root", ResNode.STATUS_PRIMARY, null), Charset.forName("windows-1252"));
        }
        try (PrintWriter summary = new PrintWriter(Files.newBufferedWriter(output.resolve("counts.txt")));
             PrintWriter resources = new PrintWriter(Files.newBufferedWriter(output.resolve("resources.tsv")));
             PrintWriter code = new PrintWriter(Files.newBufferedWriter(output.resolve("code.txt")));
             PrintWriter rooms = new PrintWriter(Files.newBufferedWriter(output.resolve("rooms.tsv")))) {
            for (Class<?> kind : GmFile.RESOURCE_KIND) {
                Object holder = game.resMap.get(kind);
                if (!(holder instanceof ResourceList)) continue;
                ResourceList<?> list = (ResourceList<?>) holder;
                Map<String, Integer> names = new HashMap<>();
                for (Object value : list) {
                    InstantiableResource<?, ?> res = (InstantiableResource<?, ?>) value;
                    resources.printf("%s\t%d\t%s%n", kind.getSimpleName(), res.getId(), res.getName());
                    names.merge(res.getName(), 1, Integer::sum);
                }
                summary.printf("%s=%d; lastId=%d; duplicate_name_groups=%d%n", kind.getSimpleName(),
                    list.size(), list.lastId, names.values().stream().filter(n -> n > 1).count());
            }
            int frames = 0, events = 0, actions = 0, instances = 0, tiles = 0;
            long rgba = 0;
            for (Sprite sprite : game.resMap.getList(Sprite.class)) {
                frames += sprite.subImages.size();
                for (java.awt.image.BufferedImage image : sprite.subImages)
                    rgba += (long) image.getWidth() * image.getHeight() * 4;
            }
            for (Script script : game.resMap.getList(Script.class)) {
                code.printf("\n// Script ID %d %s\n%s\n", script.getId(), script.getName(), script.getCode());
            }
            for (GmObject object : game.resMap.getList(GmObject.class)) {
                for (MainEvent main : object.mainEvents) for (Event event : main.events) {
                    events++;
                    actions += event.actions.size();
                    code.printf("\n// Object ID %d %s event %d:%d\n", object.getId(), object.getName(), event.mainId, event.id);
                    for (Action action : event.actions) for (Argument arg : action.getArguments())
                        code.println(arg.getVal());
                }
            }
            for (Room room : game.resMap.getList(Room.class)) {
                instances += room.instances.size();
                tiles += room.tiles.size();
                rooms.printf("%d\t%s\t%s%n", room.getId(), room.getName(), room.properties);
                code.printf("\n// Room ID %d\n%s\n", room.getId(), room.getCode());
                for (Instance instance : room.instances) code.println(instance.getCreationCode());
            }
            for (Include include : game.includes) {
                summary.printf("include=%s; declared_bytes=%d; actual_bytes=%d%n", include.filename,
                    include.size, include.data == null ? 0 : include.data.length);
                if (include.data != null)
                    Files.write(output.resolve("include-" + game.includes.indexOf(include) + ".bin"),
                        include.data, StandardOpenOption.CREATE_NEW);
            }
            summary.printf("sprite_frames=%d\nsprite_rgba_bytes=%d\nobject_events=%d\nactions=%d\nroom_instances=%d\nroom_tiles=%d\ntriggers=%d\nconstants=%d\nincludes=%d\npackages=%d%n",
                frames, rgba, events, actions, instances, tiles, game.triggers.size(),
                game.constants.size(), game.includes.size(), game.packages.size());
        }
    }
}
